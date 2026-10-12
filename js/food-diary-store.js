/* Local IndexedDB only. Source snapshots survive menu updates. */
(function(){'use strict';const F=window.GetMacrosFood;let dbPromise;
 function open(){if(!dbPromise)dbPromise=new Promise((resolve,reject)=>{const request=indexedDB.open('getmacros-diary',1);request.onupgradeneeded=()=>{const db=request.result;const entries=db.createObjectStore('entries',{keyPath:'id'});entries.createIndex('date','date');db.createObjectStore('recipes',{keyPath:'id'});db.createObjectStore('settings',{keyPath:'id'});};request.onsuccess=()=>resolve(request.result);request.onerror=()=>{dbPromise=null;reject(Error('Private browser storage is unavailable. Try another browser or export before changing browser settings.'));};request.onblocked=()=>reject(Error('Close other GetMacros diary tabs and try again.'));});return dbPromise;}
 async function tx(store,mode,operation){const db=await open();return new Promise((resolve,reject)=>{const transaction=db.transaction(store,mode),object=transaction.objectStore(store);let result;try{const request=operation(object);if(request){request.onsuccess=()=>result=request.result;}}catch(e){transaction.abort();reject(e);return;}transaction.oncomplete=()=>resolve(result);transaction.onerror=()=>reject(transaction.error||Error('Could not save. Your previous entries are unchanged.'));transaction.onabort=()=>reject(transaction.error||Error('Could not save this change.'));});}
 async function list(date){const rows=await tx('entries','readonly',s=>s.index('date').getAll(F.date(date)));return rows.sort((a,b)=>String(a.savedAt||'').localeCompare(String(b.savedAt||''))||a.id.localeCompare(b.id));}
 async function lastLoggedDate(before=F.today()){const cursor=await tx('entries','readonly',s=>s.index('date').openKeyCursor(IDBKeyRange.upperBound(F.date(before)),'prev'));return cursor?.key||null;}
 async function loggedDayCount(limit=3){
  if(!Number.isInteger(limit)||limit<1||limit>365)throw Error('Choose a valid day-count limit.');
  const db=await open();return new Promise((resolve,reject)=>{
   const transaction=db.transaction('entries','readonly'),request=transaction.objectStore('entries').index('date').openKeyCursor(null,'nextunique');let count=0;
   request.onsuccess=()=>{if(request.result){count++;if(count<limit)request.result.continue();}};
   transaction.oncomplete=()=>resolve(count);transaction.onerror=()=>reject(transaction.error||Error('Could not read the diary dates.'));
  });
 }
 async function add(snapshot,{date=F.today(),occasion='Lunch',note='',operationId=crypto.randomUUID()}={}){F.date(date);if(!snapshot?.recordId||!snapshot.nutrients||!['Breakfast','Lunch','Dinner','Snack'].includes(occasion))throw Error('Review the food and meal before saving.');const row={id:operationId,date,occasion,note:String(note).slice(0,1000),timezone:Intl.DateTimeFormat().resolvedOptions().timeZone||'local',savedAt:new Date().toISOString(),snapshot:JSON.parse(JSON.stringify(snapshot))};await tx('entries','readwrite',s=>s.put(row));return row;}
 async function remove(id){const previous=await tx('entries','readonly',s=>s.get(id));await tx('entries','readwrite',s=>s.delete(id));return previous;}
 async function update(row){F.date(row.date);await tx('entries','readwrite',s=>s.put(row));return row;}
 async function exportData(){return {schemaVersion:1,exportedAt:new Date().toISOString(),entries:await tx('entries','readonly',s=>s.getAll()),recipes:await tx('recipes','readonly',s=>s.getAll()),favorites:(await tx('settings','readonly',s=>s.get('favorites')))?.value||[]};}
 async function clear(){const db=await open();return new Promise((resolve,reject)=>{const t=db.transaction(['entries','recipes','settings'],'readwrite');for(const store of ['entries','recipes','settings'])t.objectStore(store).clear();t.oncomplete=resolve;t.onerror=()=>reject(t.error);});}
 async function importData(data){F.validateExport(data);const db=await open();return new Promise((resolve,reject)=>{const t=db.transaction(['entries','recipes','settings'],'readwrite');data.entries.forEach(r=>t.objectStore('entries').put(r));data.recipes.forEach(r=>t.objectStore('recipes').put(r));if(data.favorites)t.objectStore('settings').put({id:'favorites',value:data.favorites});t.oncomplete=resolve;t.onerror=()=>reject(t.error);});}
 const recipes=()=>tx('recipes','readonly',s=>s.getAll());
 const saveRecipe=r=>tx('recipes','readwrite',s=>s.put(r));
 async function copyMeal(entries,{date:targetDate=F.today(),occasion='Lunch',copyNotes=false,operationId=crypto.randomUUID()}={}){
  F.date(targetDate);
  if(!Array.isArray(entries)||!entries.length||entries.length>100)throw Error('Choose a meal with between 1 and 100 foods.');
  if(!['Breakfast','Lunch','Dinner','Snack'].includes(occasion)||typeof copyNotes!=='boolean'||typeof operationId!=='string'||!/^[a-zA-Z0-9-]{1,100}$/.test(operationId))throw Error('Review the meal and destination before copying.');
  const savedAt=new Date().toISOString(),timezone=Intl.DateTimeFormat().resolvedOptions().timeZone||'local';
  const rows=entries.map((entry,index)=>{
   F.validateSnapshot(entry.snapshot);F.date(entry.date);
   if(!['Breakfast','Lunch','Dinner','Snack'].includes(entry.occasion))throw Error('The original meal is invalid. Nothing was copied.');
   return {id:operationId+':'+String(index).padStart(3,'0'),date:targetDate,occasion,note:copyNotes?String(entry.note||'').slice(0,1000):'',timezone,savedAt,
    copiedFrom:{date:entry.date,occasion:entry.occasion},snapshot:JSON.parse(JSON.stringify(entry.snapshot))};
  });
  const db=await open();
  return new Promise((resolve,reject)=>{
   const transaction=db.transaction('entries','readwrite'),store=transaction.objectStore('entries');
   for(const row of rows)store.put(row);
   transaction.oncomplete=()=>resolve(rows);
   transaction.onerror=()=>reject(transaction.error||Error('The meal could not be copied. Your previous entries are unchanged.'));
   transaction.onabort=()=>reject(transaction.error||Error('The meal could not be copied. Your previous entries are unchanged.'));
  });
 }
 window.GetMacrosDiary={open,list,lastLoggedDate,loggedDayCount,add,remove,update,copyMeal,exportData,importData,clear,recipes,saveRecipe,setting:async(id,value)=>value===undefined?tx('settings','readonly',s=>s.get(id)).then(r=>r?.value):tx('settings','readwrite',s=>s.put({id,value}))};
})();
