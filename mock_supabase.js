window.supabase={createClient:()=>{
 let session=JSON.parse(localStorage.getItem('mock-sess')||'null');
 const save=s=>{session=s;localStorage.setItem('mock-sess',JSON.stringify(s))};
 return {auth:{
  getSession:async()=>({data:{session}}),
  signInWithPassword:async({email,password})=>{const r=await __srv('login',[email,password]);if(r.error)return{error:{message:r.error}};save(r.session);return{data:{session}}},
  signUp:async({email,password})=>{const r=await __srv('signup',[email,password]);if(r.error)return{error:{message:r.error}};save(r.session);return{data:{session}}},
  onAuthStateChange:()=>{},resetPasswordForEmail:async()=>({}),
  signOut:async()=>{localStorage.removeItem('mock-sess')}},
 from:()=>({upsert:async row=>{if(!navigator.onLine)return{error:{message:'Failed to fetch'}};await __srv('upsert',[session.user.id,row]);return{error:null}},
   select:()=>({order:()=>({range:async(a,b)=>{if(!navigator.onLine)return{error:{message:'Failed to fetch'}};return{data:await __srv('list',[session.user.id,a,b])}}})})}),
 channel:()=>({on(){return this},subscribe(){}})}}};
