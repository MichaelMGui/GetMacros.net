import Foundation
import UIKit
import UniformTypeIdentifiers
import Capacitor

/// This bridge never accepts arbitrary paths and never sends diary data to a server.
@objc(GetMacrosArchivePlugin)
public final class GetMacrosArchivePlugin: CAPPlugin, CAPBridgedPlugin, UIDocumentPickerDelegate {
    public let identifier = "GetMacrosArchivePlugin"
    public let jsName = "GetMacrosArchive"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "save", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "read", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "clear", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "exportBackup", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "importBackup", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "share", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "openExternal", returnType: CAPPluginReturnPromise)
    ]
    private var pendingPicker: CAPPluginCall?
    private var temporaryExport: URL?
    private let limit = 20_000_000

    private func localOrigin(_ call: CAPPluginCall) -> Bool {
        guard let url = bridge?.webView?.url, url.scheme == "capacitor", url.host == "localhost" else {
            call.reject("This action is available only in the bundled GetMacros app.")
            return false
        }
        return true
    }

    private func archiveURL() throws -> URL {
        let support = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
        var directory = support.appendingPathComponent("GetMacros", isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        var values = URLResourceValues()
        values.isExcludedFromBackup = true // Explicit user-created Files exports are the migration path.
        try directory.setResourceValues(values)
        return directory.appendingPathComponent("diary-v1.json", isDirectory: false)
    }

    private func checkedJSON(_ json: String?) throws -> Data {
        guard let json = json, let data = json.data(using: .utf8), data.count <= limit,
              let value = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              value["schemaVersion"] as? Int == 1,
              value["entries"] is [[String: Any]], value["recipes"] is [[String: Any]] else {
            throw NSError(domain: "GetMacrosBackup", code: 1, userInfo: [NSLocalizedDescriptionKey: "Choose a GetMacros JSON backup smaller than 20 MB."])
        }
        return data // Full record validation is shared with food-core.js before imports or writes.
    }

    @objc func save(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        do { try checkedJSON(call.getString("json")).write(to: archiveURL(), options: [.atomic, .completeFileProtection]); call.resolve() }
        catch { call.reject("The local app archive could not be saved.", nil, error) }
    }
    @objc func read(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        do { let url = try archiveURL(); guard FileManager.default.fileExists(atPath: url.path) else { call.resolve(["json": ""]); return }
            let data = try Data(contentsOf: url); guard data.count <= limit, let json = String(data: data, encoding: .utf8) else { throw CocoaError(.fileReadCorruptFile) }; _ = try checkedJSON(json); call.resolve(["json": json])
        } catch { call.reject("The local app archive could not be read.", nil, error) }
    }
    @objc func clear(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        do { let url = try archiveURL(); if FileManager.default.fileExists(atPath: url.path) { try FileManager.default.removeItem(at: url) }; call.resolve() }
        catch { call.reject("The local app archive could not be deleted.", nil, error) }
    }
    @objc func exportBackup(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        do { let data = try checkedJSON(call.getString("json"));
            DispatchQueue.main.async { [weak self] in
                guard let self = self else { call.reject("The app is unavailable."); return }
                guard self.pendingPicker == nil else { call.reject("Close the current file picker first."); return }
                let url = FileManager.default.temporaryDirectory.appendingPathComponent("getmacros-diary-backup.json")
                do { try data.write(to: url, options: [.atomic, .completeFileProtection]) }
                catch { call.reject("The backup could not be prepared.", nil, error); return }
                self.temporaryExport = url; self.pendingPicker = call
                let picker = UIDocumentPickerViewController(forExporting: [url], asCopy: true)
                picker.delegate = self; self.bridge?.viewController?.present(picker, animated: true)
            }
        } catch { call.reject(error.localizedDescription) }
    }
    @objc func importBackup(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { call.reject("The app is unavailable."); return }
            guard self.pendingPicker == nil else { call.reject("Close the current file picker first."); return }
            self.pendingPicker = call
            let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.json], asCopy: true)
            picker.allowsMultipleSelection = false; picker.delegate = self
            self.bridge?.viewController?.present(picker, animated: true)
        }
    }
    public func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        guard let call = pendingPicker else { return }; pendingPicker = nil
        defer { clearTemporaryExport() }
        if temporaryExport != nil { call.resolve(["saved": true]); return }
        guard let url = urls.first else { call.resolve(["cancelled": true]); return }
        let access = url.startAccessingSecurityScopedResource(); defer { if access { url.stopAccessingSecurityScopedResource() } }
        do { let data = try Data(contentsOf: url, options: .mappedIfSafe)
            guard data.count <= limit, let json = String(data: data, encoding: .utf8) else { throw CocoaError(.fileReadCorruptFile) }
            _ = try checkedJSON(json); call.resolve(["json": json])
        } catch { call.reject("That file is not a supported GetMacros backup. Your diary is unchanged.", nil, error) }
    }
    public func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
        pendingPicker?.resolve(["cancelled": true]); pendingPicker = nil; clearTemporaryExport()
    }
    private func clearTemporaryExport() { if let url = temporaryExport { try? FileManager.default.removeItem(at: url) }; temporaryExport = nil }

    @objc func share(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        let title = String((call.getString("title") ?? "GetMacros").prefix(200)), text = String((call.getString("text") ?? "").prefix(2000))
        var items: [Any] = [title]; if !text.isEmpty { items.append(text) }
        if let raw = call.getString("url"), !raw.isEmpty {
            guard let url = URL(string: raw), url.scheme == "https", url.host == "getmacros.net" else { call.reject("Only public GetMacros links can be shared from this action."); return }; items.append(url)
        }
        DispatchQueue.main.async { [weak self] in
            guard let controller = self?.bridge?.viewController else { call.reject("Sharing is unavailable."); return }
            let share = UIActivityViewController(activityItems: items, applicationActivities: nil)
            if let popover = share.popoverPresentationController { popover.sourceView = controller.view; popover.sourceRect = CGRect(x: controller.view.bounds.midX, y: controller.view.bounds.midY, width: 1, height: 1) }
            share.completionWithItemsHandler = { _, completed, _, error in if let error = error { call.reject("The item could not be shared.", nil, error) } else { call.resolve(["completed": completed]) } }
            controller.present(share, animated: true)
        }
    }
    @objc func openExternal(_ call: CAPPluginCall) {
        guard localOrigin(call) else { return }
        guard let raw = call.getString("url"), let url = URL(string: raw), ["https", "mailto", "tel"].contains(url.scheme?.lowercased() ?? "") else { call.reject("This link cannot be opened."); return }
        DispatchQueue.main.async { UIApplication.shared.open(url, options: [:]) { success in call.resolve(["opened": success]) } }
    }
}
