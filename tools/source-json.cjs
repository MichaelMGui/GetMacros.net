/* Source-separated test/build reader for plain or deterministic gzip JSON. */
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
function resolve(file){if(fs.existsSync(file))return file;if(fs.existsSync(file+'.gz'))return file+'.gz';throw Error('Missing source data: '+file);}
function read(file){const target=resolve(file),bytes=fs.readFileSync(target);return JSON.parse((target.endsWith('.gz')?zlib.gunzipSync(bytes):bytes).toString('utf8'));}
function fileResponse(root,url,onBytes=()=>{}){const file=path.join(root,decodeURIComponent(new URL(url,'https://getmacros.test').pathname));if(!fs.existsSync(file))return new Response('',{status:404});const bytes=fs.readFileSync(file);onBytes(bytes.length);return new Response(bytes,{status:200});}
module.exports={read,resolve,fileResponse};
