/* Unamia — synchronisation en ligne via Supabase (connexion e-mail + mot de passe) */
(function(){
const URL_='https://dakfqfrihtppnecrzmrp.supabase.co';
const KEY_='sb_publishable_RmjBSyr-ehFI1abh2P84hQ_0pQ3q28H';
const LASTUID='carnet-ongles-v1-lastuid';
const sb=window.supabase.createClient(URL_,KEY_,{auth:{persistSession:true,autoRefreshToken:true,storageKey:'unamia-auth'}});
let email='';

function codeOf(e){const s=e&&(e.status||e.code);
  if(s===401||s==='PGRST301'||/jwt/i.test(e&&e.message||''))return 'auth';
  if(s==='42501'||s===403)return 'denied';
  if(s==='23514'||s==='22P02'||s===400)return 'invalid_argument';
  return 'network'}
function mkErr(e){const x=new Error(e&&e.message||'erreur');x.code=codeOf(e);return x}
function frMsg(m){m=String(m||'');
  if(/invalid login/i.test(m))return 'E-mail ou mot de passe incorrect.';
  if(/already registered|already been registered/i.test(m))return 'Un compte existe déjà avec cet e-mail : utilisez « Se connecter ».';
  if(/password.*(at least|short|weak)/i.test(m))return 'Mot de passe trop court (8 caractères minimum).';
  if(/email not confirmed/i.test(m))return 'Adresse e-mail pas encore confirmée : cliquez sur le lien reçu par e-mail.';
  if(/rate limit|too many/i.test(m))return 'Trop de tentatives, réessayez dans quelques minutes.';
  if(/fetch|network/i.test(m))return 'Pas de connexion internet.';
  return m||'Erreur inconnue.'}

function makeCol(uid){
  return {
    doc(id){return {set:async body=>{
      const {error}=await sb.from('docs').upsert({user_id:uid,id,data:body,updated_at:new Date().toISOString()},{onConflict:'user_id,id'});
      if(error)throw mkErr(error)}}},
    onSnapshot(cb,errCb){
      let busy=false,again=false,fails=0;
      async function fetchAll(){let rows=[],from=0;
        for(;;){const {data,error}=await sb.from('docs').select('id,data').order('id').range(from,from+999);
          if(error)throw error;rows=rows.concat(data||[]);if(!data||data.length<1000)break;from+=1000}
        return rows}
      async function pull(){
        if(busy){again=true;return}busy=true;
        try{const rows=await fetchAll();fails=0;
          cb({docs:rows.map(r=>({id:r.id,data:()=>r.data})),metadata:{fromCache:false}})}
        catch(e){fails++;if(codeOf(e)==='auth'&&fails>2&&errCb)errCb(mkErr(e))}
        finally{busy=false;if(again){again=false;pull()}}}
      pull();
      try{sb.channel('docs-'+uid).on('postgres_changes',{event:'*',schema:'public',table:'docs',filter:'user_id=eq.'+uid},()=>pull()).subscribe()}catch(e){}
      document.addEventListener('visibilitychange',()=>{if(!document.hidden)pull()});
      window.addEventListener('focus',pull);window.addEventListener('online',pull);
      setInterval(pull,30000);
    }};
}

/* ---- écran de connexion ---- */
const CSS=`#sbLogin{position:fixed;inset:0;z-index:200;background:var(--bg,#F8F4EE);display:flex;align-items:center;justify-content:center;padding:20px;overflow:auto}
#sbLogin .box{background:#fff;border:1px solid var(--line,#E8E0D4);border-radius:18px;padding:32px 28px;width:100%;max-width:380px;box-shadow:0 10px 40px rgba(58,42,34,.08);text-align:center}
#sbLogin img{width:84px;height:84px;border-radius:50%;margin-bottom:10px}
#sbLogin h2{font-family:'Cormorant Garamond',serif;font-size:30px;margin:0 0 2px;letter-spacing:.14em;color:var(--ink,#3A2A22);font-weight:600}
#sbLogin p.s{margin:0 0 20px;font-size:13px;color:var(--muted,#8B7D70)}
#sbLogin label{display:block;text-align:left;font-size:12px;color:var(--muted,#8B7D70);margin:10px 0 4px}
#sbLogin input{width:100%;box-sizing:border-box;padding:11px 12px;border:1px solid var(--line,#E8E0D4);border-radius:10px;font:inherit;font-size:15px;color:#3A2A22;background:#fff}
#sbLogin button.p{width:100%;margin-top:18px;padding:12px;border:0;border-radius:10px;background:#4B3427;color:#fff;font:inherit;font-weight:500;font-size:15px;cursor:pointer}
#sbLogin button.p:disabled{opacity:.6}
#sbLogin button.l{background:none;border:0;color:#8B7D70;font:inherit;font-size:13px;margin-top:12px;cursor:pointer;text-decoration:underline}
#sbLogin .m{margin-top:12px;font-size:13px;min-height:18px;color:#A33}#sbLogin .m.ok{color:#5F7F66}`;
function ui(mode){return new Promise(resolve=>{
  if(!document.getElementById('sbCss')){const s=document.createElement('style');s.id='sbCss';s.textContent=CSS;document.head.appendChild(s)}
  const el=document.createElement('div');el.id='sbLogin';document.body.appendChild(el);
  const logo=(document.getElementById('logo')||{}).src||'';
  let m=mode||'in';
  function draw(){
    const t={in:'Se connecter',up:'Créer mon compte',reset:'Envoyer le lien',newpw:'Enregistrer le mot de passe'}[m];
    el.innerHTML=`<form class="box" novalidate>${logo?`<img src="${logo}" alt="">`:''}<h2>UNAMIA</h2><p class="s">${m==='in'?'Connectez-vous pour retrouver votre carnet sur tous vos appareils.':m==='up'?'Créez votre accès (une seule fois).':m==='reset'?'Entrez votre e-mail pour recevoir un lien.':'Choisissez un nouveau mot de passe.'}</p>
      ${m!=='newpw'?'<label>Adresse e-mail</label><input id="sbE" type="email" autocomplete="email" inputmode="email" autocapitalize="off">':''}
      ${m==='in'||m==='up'||m==='newpw'?`<label>${m==='newpw'?'Nouveau mot de passe':'Mot de passe'}${m!=='in'?' (8 caractères minimum)':''}</label><input id="sbP" type="password" autocomplete="${m==='in'?'current-password':'new-password'}">`:''}
      <button class="p" type="submit">${t}</button><div class="m" id="sbM"></div>
      ${m==='in'?'<button type="button" class="l" data-m="up">Première fois ? Créer mon compte</button><br><button type="button" class="l" data-m="reset">Mot de passe oublié</button>':m!=='newpw'?'<button type="button" class="l" data-m="in">Retour à la connexion</button>':''}</form>`;
    const $=id=>el.querySelector(id),msg=(x,ok)=>{const d=$('#sbM');d.textContent=x;d.className='m'+(ok?' ok':'')};
    el.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{m=b.dataset.m;draw()});
    const em=$('#sbE');if(em){em.value=email;setTimeout(()=>em.focus(),50)}
    el.querySelector('form').onsubmit=async ev=>{ev.preventDefault();
      const btn=$('button.p');const e=em?em.value.trim():'',p=$('#sbP')?$('#sbP').value:'';
      if(m!=='newpw'&&!/^\S+@\S+\.\S+$/.test(e))return msg('Adresse e-mail invalide.');
      if(m!=='reset'&&p.length<(m==='in'?1:8))return msg(m==='in'?'Entrez votre mot de passe.':'Mot de passe trop court (8 caractères minimum).');
      btn.disabled=true;msg('…',true);email=e||email;
      try{
        if(m==='in'){const {data,error}=await sb.auth.signInWithPassword({email:e,password:p});if(error)throw error;el.remove();resolve(data.session)}
        else if(m==='up'){const {data,error}=await sb.auth.signUp({email:e,password:p});if(error)throw error;
          if(data.session){el.remove();resolve(data.session)}else{m='in';draw();el.querySelector('#sbM').className='m ok';el.querySelector('#sbM').textContent='Compte créé. Confirmez votre adresse e-mail via le lien reçu, puis connectez-vous.'}}
        else if(m==='reset'){const {error}=await sb.auth.resetPasswordForEmail(e,{redirectTo:location.origin+location.pathname});if(error)throw error;msg('Lien envoyé : vérifiez votre boîte e-mail (et les courriers indésirables).',true)}
        else if(m==='newpw'){const {error}=await sb.auth.updateUser({password:p});if(error)throw error;const {data}=await sb.auth.getSession();history.replaceState(null,'',location.pathname);el.remove();resolve(data.session)}
      }catch(err){msg(frMsg(err.message))}
      btn.disabled=false};
  }
  draw();
})}

async function open(){
  const recovery=/type=recovery/.test(location.hash);
  let session=null;
  try{const r=await sb.auth.getSession();session=r.data&&r.data.session}catch(e){}
  if(recovery)session=await ui('newpw');
  if(!session){
    const last=localStorage.getItem(LASTUID);
    if(last&&!navigator.onLine)return {uid:last,col:makeCol(last),email:localStorage.getItem(LASTUID+'-mail')||''};
    session=await ui('in');
  }
  const u=session.user;email=u.email||'';
  try{localStorage.setItem(LASTUID,u.id);localStorage.setItem(LASTUID+'-mail',email)}catch(e){}
  sb.auth.onAuthStateChange(ev=>{if(ev==='SIGNED_OUT')location.reload()});
  return {uid:u.id,col:makeCol(u.id),email};
}
window.SB_BACKEND={open,signOut:async()=>{try{localStorage.removeItem(LASTUID)}catch(e){}await sb.auth.signOut();location.reload()}};
})();
