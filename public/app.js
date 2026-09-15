const dialog=document.getElementById('browser-dialog');
const input=document.getElementById('page-link');
const status=document.querySelector('.copy-status');
document.querySelectorAll('[data-browser]').forEach(button=>button.addEventListener('click',()=>{
 input.value=new URL(button.dataset.permalink,location.origin).href;status.textContent='';
 if(typeof dialog.showModal==='function')dialog.showModal();else{dialog.setAttribute('open','');dialog.style.position='fixed';dialog.style.top='15%';dialog.style.zIndex='50';}
}));
document.getElementById('close-dialog').addEventListener('click',()=>{if(typeof dialog.close==='function')dialog.close();else dialog.removeAttribute('open');});
dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
document.getElementById('copy-link').addEventListener('click',async()=>{
 try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(input.value);}else{input.focus();input.select();input.setSelectionRange(0,input.value.length);if(!document.execCommand('copy'))throw Error('copy');}status.textContent='链接已复制，可粘贴到浏览器打开。';}
 catch{input.focus();input.select();status.textContent='请长按或选中上方链接，手动复制。';}
});
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){document.querySelectorAll('.toc nav a').forEach(a=>a.classList.toggle('active',a.hash==='#'+entry.target.id));}});},{rootMargin:'-100px 0px -65% 0px'});document.querySelectorAll('.report-section').forEach(section=>observer.observe(section));}
