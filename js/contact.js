/* A local email draft. Nothing is submitted to a server or stored on this page. */
(()=>{
 const form=document.querySelector('#contact-form');if(!form)return;
 form.querySelectorAll('button[disabled]').forEach(button=>button.disabled=false);
 const email='getmacros.net@outlook.com',topic=document.querySelector('#contact-topic'),message=document.querySelector('#contact-message'),hint=document.querySelector('#contact-hint'),status=document.querySelector('#contact-draft-status');
 const topics={question:['A question for GetMacros','Tell me what you’d like to know. Please leave out private health details.'],idea:['An idea for GetMacros','What were you trying to do, and what would make it easier?'],problem:['Something to fix on GetMacros','Include the page link, what you tried and what happened. For a nutrition number, add the restaurant and menu item.']};
 const draft=document.querySelector('#contact-email-draft');
 function updateDraft(){draft.href=`mailto:${email}?subject=${encodeURIComponent(topics[topic.value][0])}&body=${encodeURIComponent(message.value.trim())}`;}
 function sync(){hint.textContent=topics[topic.value][1];status.textContent='';updateDraft();}
 message.addEventListener('input',updateDraft);updateDraft();
 topic.addEventListener('change',sync);
 document.querySelectorAll('[data-contact-topic]').forEach(button=>button.addEventListener('click',event=>{
  event.preventDefault();topic.value=button.dataset.contactTopic;sync();
  const section=document.querySelector('#contact-draft'),header=document.querySelector('.site-header');
  const top=scrollY+section.getBoundingClientRect().top-(header?.getBoundingClientRect().bottom||0)-16;
  // Focus immediately without racing a smooth scroll against the phone keyboard.
  scrollTo({top:Math.max(0,top),behavior:'instant'});message.focus({preventScroll:true});
 }));
 const text=()=>`To: ${email}\nSubject: ${topics[topic.value][0]}\n\n${message.value.trim()}`;
 async function copy(value,target){
  try{await navigator.clipboard.writeText(value);target.textContent='Copied. Paste it into your email app.';}
  catch(_){const box=document.querySelector('#contact-copy-fallback'),area=document.querySelector('#contact-copy-text');box.hidden=false;area.value=value;area.focus();area.select();target.textContent='Select and copy the details below.';}
 }
 document.querySelector('[data-copy-address]').addEventListener('click',()=>copy(email,document.querySelector('#contact-copy-status')));
 document.querySelector('[data-copy-message]').addEventListener('click',()=>{if(form.reportValidity())copy(text(),status);});
 draft.addEventListener('click',event=>{if(!form.reportValidity()){event.preventDefault();return;}updateDraft();status.textContent='Your message is ready for your email app. Nothing has been sent from this page.';});
 form.addEventListener('submit',event=>{event.preventDefault();draft.click();});
})();
