/* ── TYPED JS ── */
new Typed('#typed-el', {
  strings:[
    'AI Engineer',
    'Data Scientist',
    'Agentic AI Developer',
    'RAG Systems Architect',
    'MLOps Engineer',
    'Kaggle Grandmaster 🏆',
  ],
  typeSpeed:55,backSpeed:32,backDelay:2000,
  loop:true,cursorChar:'|',smartBackspace:true
});

console.log('✅ Typed.js initialized');

/* ── MOBILE NAV ── */
const ham=document.getElementById('ham');
const navMenu=document.getElementById('navMenu');
ham.addEventListener('click',()=>navMenu.classList.toggle('open'));
navMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>navMenu.classList.remove('open')));

console.log('✅ Mobile nav initialized');

/* ── ACTIVE NAV HIGHLIGHT ── */
const secs=document.querySelectorAll('section[id]');
const navAs=document.querySelectorAll('.nav-menu a');
window.addEventListener('scroll',()=>{
  let cur='';
  secs.forEach(s=>{if(window.scrollY>=s.offsetTop-200)cur=s.id});
  navAs.forEach(a=>{
    a.classList.toggle('active',a.getAttribute('href')==='#'+cur);
  });
},{ passive:true });

/* ── SCROLL REVEAL ── */
const revEls=document.querySelectorAll('.reveal');
const io=new IntersectionObserver(entries=>{
  entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('vis');io.unobserve(e.target)}});
},{threshold:.08,rootMargin:'0px 0px -50px 0px'});
revEls.forEach(el=>io.observe(el));

console.log('✅ Scroll reveal initialized');

/* ── RESUME DOWNLOAD ── */
function downloadResume(){
  const url='YOUR_RESUME_PDF_URL_HERE';
  console.log('📄 Downloading resume...');
  const a=document.createElement('a');
  a.href=url;a.download='Asadullah_Shehbaz_Resume.pdf';a.target='_blank';
  document.body.appendChild(a);a.click();document.body.removeChild(a);
}
document.getElementById('resumeBtn')?.addEventListener('click',downloadResume);

/* ── CHATBOT ── */
const API_ENDPOINT = '/chat';
console.log(`💬 Chatbot API endpoint: ${API_ENDPOINT}`);
  
const chatFab=document.getElementById('chatFab');
const chatPanel=document.getElementById('chatPanel');
const cpClose=document.getElementById('cpClose');
const cpMsgs=document.getElementById('cpMsgs');
const cpInput=document.getElementById('cpInput');
const cpSend=document.getElementById('cpSend');
const cpQuick=document.getElementById('cpQuick');

let isOpen=false;

function toggleChat(state){
  isOpen = state !== undefined ? state : !isOpen;
  chatPanel.classList.toggle('open',isOpen);
  chatFab.classList.toggle('open',isOpen);
  chatFab.querySelector('.ic-chat').style.display = isOpen ? 'none' : 'block';
  chatFab.querySelector('.ic-close').style.display = isOpen ? 'block' : 'none';
  if(isOpen) {
    cpInput.focus();
    console.log('💬 Chat opened');
  } else {
    console.log('💬 Chat closed');
  }
}

chatFab.addEventListener('click',()=>toggleChat());
cpClose.addEventListener('click',()=>toggleChat(false));

function nowTime(){
  return new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
}

function addMsg(text,role){
  const div=document.createElement('div');
  div.className=`cm cm-${role}`;
  div.innerHTML=`<div class="cm-bubble">${text}</div><div class="cm-time">${nowTime()}</div>`;
  div.style.animationDelay='0s';
  cpMsgs.appendChild(div);
  cpMsgs.scrollTop=cpMsgs.scrollHeight;
  console.log(`💬 Added ${role} message: ${text.substring(0,50)}...`);
}

function showTyping(){
  const d=document.createElement('div');
  d.className='cm typing-row';d.id='typingEl';
  d.innerHTML=`<div class="typing-bub"><span></span><span></span><span></span></div>`;
  cpMsgs.appendChild(d);
  cpMsgs.scrollTop=cpMsgs.scrollHeight;
  console.log('⌨️ Showing typing indicator...');
}

function hideTyping(){
  const el = document.getElementById('typingEl');
  if(el) el.remove();
  console.log('✅ Typing indicator removed');
}

async function sendMsg(text){
  if(!text.trim()) {
    console.warn('⚠️ Empty message ignored');
    return;
  }
  
  console.log(`💬 Sending message: "${text}"`);
  cpQuick.style.display='none';
  cpInput.value='';
  cpSend.disabled=true;
  addMsg(text,'user');
  showTyping();

  try{
    console.log(`📡 Fetching ${API_ENDPOINT}...`);
    const res=await fetch(API_ENDPOINT,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:text})
    });
    
    console.log(`📡 Response status: ${res.status}`);
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const data=await res.json();
    console.log(`📡 Response data:`, data);
    
    hideTyping();
    const reply = data.response || data.answer || data.message || 'No response from server';
    addMsg(reply,'bot');
    console.log(`✅ Bot reply sent (${reply.length} chars)`);
    
  } catch(err){
    console.error('❌ Chat error:', err);
    hideTyping();
    addMsg('⚠️ Unable to connect to the API. Check your endpoint configuration.','bot');
  } finally {
    cpSend.disabled=false;
    console.log('💬 Chat request completed');
  }
}

cpSend.addEventListener('click',()=>sendMsg(cpInput.value));
cpInput.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){
    e.preventDefault();
    console.log('⌨️ Enter pressed, sending message');
    sendMsg(cpInput.value);
  }
});

function quickSend(t){
  console.log(`🔘 Quick reply clicked: "${t}"`);
  sendMsg(t);
}

console.log('✅ Chatbot initialized and ready');
console.log('💡 Open console (F12) to see chat logs');