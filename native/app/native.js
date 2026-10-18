/* App-only integration. No dietary information is sent to a service. */
(function(){'use strict';
 if(!window.Capacitor?.isNativePlatform?.())return;
 document.documentElement.classList.add('gm-native');
 const native=capacitorExports.registerPlugin('GetMacrosArchive');
 const rawFetch=window.fetch.bind(window),foodPrefix='/data/branded-foods/';
 const sameApp=url=>url.protocol===location.protocol&&url.hostname===location.hostname&&url.port===location.port;
 let database;
 const cacheDB=()=>database||(database=new Promise((resolve,reject)=>{const r=indexedDB.open('getmacros-native-food-cache',1);r.onupgradeneeded=()=>r.result.createObjectStore('responses',{keyPath:'path'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);}));
 async function cached(path,value){const db=await cacheDB();return new Promise((resolve,reject)=>{const tx=db.transaction('responses',value?'readwrite':'readonly'),store=tx.objectStore('responses'),r=value?store.put({path,...value}):store.get(path);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});}
 async function prune(){const db=await cacheDB();const tx=db.transaction('responses','readwrite'),s=tx.objectStore('responses'),r=s.getAll();r.onsuccess=()=>{const rows=r.result.sort((a,b)=>b.saved-a.saved);let size=0;for(const row of rows){size+=row.bytes.byteLength;if(size>64*1024*1024)s.delete(row.path);}};}
 window.fetch=async function(input,init){
  const url=new URL(typeof input==='string'?input:input.url,location.href);
  const method=String(init?.method||(typeof input==='object'?input.method:'GET')||'GET').toUpperCase();
  if(sameApp(url)&&url.pathname.startsWith(foodPrefix)&&method==='GET'){
   const path=url.pathname+url.search;
   try{const response=await rawFetch('https://getmacros.net'+path,{...init,credentials:'omit',referrerPolicy:'no-referrer'});if(!response.ok)throw Error('Food source unavailable');const bytes=await response.arrayBuffer();if(bytes.byteLength<=12*1024*1024){await cached(path,{bytes,contentType:response.headers.get('content-type')||'application/json',saved:Date.now()}).catch(()=>{});prune().catch(()=>{});}return new Response(bytes,{status:200,headers:{'Content-Type':response.headers.get('content-type')||'application/json'}});}
   catch(error){const previous=await cached(path).catch(()=>null);if(previous)return new Response(previous.bytes,{status:200,headers:{'Content-Type':previous.contentType,'X-GetMacros-Offline':'cached'}});throw error;}
  }
  return rawFetch(input,init);
 };
 // No service worker or remote executable code inside the app.
 if('serviceWorker' in navigator)navigator.serviceWorker.register=()=>Promise.reject(Error('The app uses bundled resources.'));
 if(!navigator.share){try{Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{const url=data?.url?new URL(data.url,location.href):null;if(url&&sameApp(url))url.href='https://getmacros.net'+url.pathname+url.search+url.hash;return native.share({title:String(data?.title||'GetMacros').slice(0,200),text:String(data?.text||'').slice(0,2000),url:url?.href||''});}});}catch{/* The rest of the diary remains usable if an OS-owned property is immutable. */}}
 let archiveTask=Promise.resolve();
 function archive(){archiveTask=archiveTask.then(async()=>{try{const data=await window.GetMacrosDiary.exportData();window.GetMacrosFood.validateExport(data);await native.save({json:JSON.stringify(data)});}catch(e){document.dispatchEvent(new CustomEvent('native-backup-error',{detail:{message:'The app backup could not be updated. Export a backup before removing the app.'}}));}});return archiveTask;}
 function message(text){const node=document.querySelector('[data-preferences-status]');if(node)node.textContent=text;}
 async function mount(){
  const store=window.GetMacrosDiary;if(!store)return;
  for(const method of ['add','update','remove','copyMeal','saveRecipe','importData']){const original=store[method];store[method]=async function(...args){const result=await original.apply(this,args);archive();return result;};}
  const originalSetting=store.setting;store.setting=async function(id,value){const result=await originalSetting.apply(this,arguments);if(value!==undefined&&id==='favorites')archive();return result;};
  const originalClear=store.clear;store.clear=async function(){await archiveTask;await native.clear();const result=await originalClear.apply(this,arguments);await archive();return result;};
  try{const data=await store.exportData();if(!data.entries.length&&!data.recipes.length&&!data.favorites.length){const previous=await native.read();if(previous.json){const restored=JSON.parse(previous.json);window.GetMacrosFood.validateExport(restored);if(restored.entries.length||restored.recipes.length||restored.favorites?.length){await store.importData(restored);location.reload();return;}}}}catch(e){message('Your diary is unchanged. A local app archive could not be restored.');}
  const area=document.querySelector('#diary-preferences [data-preferences-status]')?.parentElement||document.querySelector('[data-diary-export]')?.parentElement;
  if(area){const group=document.createElement('div');group.className='native-backups';
   const introduction=area.querySelector('header + p');if(introduction)introduction.textContent='Stored on this device. Export a backup before removing the app.';
   const exportButton=document.createElement('button');exportButton.type='button';exportButton.textContent='Save backup to Files';exportButton.addEventListener('click',async()=>{try{const data=await store.exportData();window.GetMacrosFood.validateExport(data);await native.exportBackup({json:JSON.stringify(data)});message('Backup prepared. Keep it private: it includes your notes.');}catch(e){message(e.message||'Backup was not saved.');}});
   const importButton=document.createElement('button');importButton.type='button';importButton.textContent='Import Safari backup';importButton.addEventListener('click',async()=>{try{const result=await native.importBackup();if(!result.json)return;const data=JSON.parse(result.json);window.GetMacrosFood.validateExport(data);if(!confirm('Import this backup? Matching entry IDs will be merged. Your existing entries remain.'))return;await store.importData(data);location.reload();}catch(e){message('That file could not be imported as a GetMacros diary backup. Your diary is unchanged.');}});
   const help=document.createElement('p');help.textContent='Safari and the app have separate storage. Export your Safari diary, then import that JSON file here.';group.append(exportButton,importButton,help);const backupArea=area.querySelector('.food-privacy-actions');if(backupArea)backupArea.replaceChildren(group);else area.append(group);
   // File pickers and native save sheets replace unreliable WKWebView blob downloads.
   const old=document.querySelector('[data-diary-export]');if(old){old.hidden=true;const legacy=old.closest('details');if(legacy)legacy.hidden=true;}const oldImport=document.querySelector('[data-diary-import]');if(oldImport)oldImport.closest('label')?.setAttribute('hidden','');
   const oldOffline=document.querySelector('[data-app-offline-status]');if(oldOffline)oldOffline.closest('details')?.setAttribute('hidden','');
  }
  document.addEventListener('visibilitychange',()=>{if(document.hidden)archive();});archive();
 }
 document.addEventListener('click',event=>{const a=event.target.closest('a[href]');if(!a)return;const url=new URL(a.href,location.href);if(sameApp(url)||url.protocol==='blob:')return;if(['https:','mailto:','tel:'].includes(url.protocol)){event.preventDefault();native.openExternal({url:url.href}).catch(()=>{});}else event.preventDefault();},true);
 // Deferred scripts execute at readyState=interactive, before later deferred diary models.
 if(document.readyState!=='complete')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
