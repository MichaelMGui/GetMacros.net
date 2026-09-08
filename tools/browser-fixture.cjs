const fs=require('node:fs'),path=require('node:path');
exports.localAssets=async page=>{
 if(process.env.GM_TEST_THEME)await page.addInitScript(t=>localStorage.setItem('gm-theme',t),process.env.GM_TEST_THEME);
 await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.hostname!=='127.0.0.1')return r.abort();const file=path.resolve('.'+decodeURIComponent(u.pathname));if(!file.startsWith(process.cwd()+path.sep)||!fs.existsSync(file))return r.fulfill({status:404,body:''});return r.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2'})[path.extname(file)]||'application/octet-stream'});});
};
