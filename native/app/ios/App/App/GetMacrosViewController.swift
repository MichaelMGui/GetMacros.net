import Capacitor

/// Plugins are registered only in the bundled, local-origin web view.
final class GetMacrosViewController: CAPBridgeViewController {
    override func capacitorDidLoad() {
        bridge?.registerPluginInstance(GetMacrosArchivePlugin())
    }
}
