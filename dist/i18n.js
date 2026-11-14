// Translate interface labels only. Source records, evidence and user input stay verbatim.
const labels = {
'Explore what’s possible.':'नए अवसर खोजें।','Ask across the library · English or Hindi':'लाइब्रेरी में खोजें · हिंदी या अंग्रेज़ी','Search collected records ↗':'संग्रहित रिकॉर्ड खोजें ↗','Inspect claims ↗':'प्रमाण देखें ↗','Name / type':'नाम / प्रकार','Check status':'जाँच की स्थिति','Find opportunities ↗':'अवसर खोजें ↗','Recent runs':'हाल की खोजें','Build research CSV ↗':'शोध CSV बनाएं ↗','Recent research':'हाल का शोध','Ask. Discover. Download.':'पूछें। खोजें। डाउनलोड करें।','Research objective · Hindi or English':'शोध का उद्देश्य · हिंदी या अंग्रेज़ी','Describe your requirements · English / Hindi':'अपनी ज़रूरत बताएं · हिंदी / अंग्रेज़ी','I’m looking for':'मुझे चाहिए','Cancel':'रद्द करें','Records':'रिकॉर्ड','Knowledge graph':'ज्ञान ग्राफ','Inspect claims':'प्रमाण देखें','Evidence':'प्रमाण','Name':'नाम','Entity type':'इकाई का प्रकार','Organization name':'संगठन का नाम','Registration type':'पंजीकरण प्रकार','Headquarters city':'मुख्यालय का शहर','Focus area':'कार्य क्षेत्र','Target region':'लक्षित क्षेत्र','Establishment year':'स्थापना वर्ष','Recent projects':'हाल की परियोजनाएँ','Funding sources':'वित्त पोषण के स्रोत','Contact email':'संपर्क ईमेल','Website url':'वेबसाइट','Last active year':'अंतिम सक्रिय वर्ष','Partnership details':'साझेदारी विवरण','Reload library':'लाइब्रेरी फिर लोड करें','Refresh sources':'स्रोत अपडेट करें','Research & fellowships':'शोध और फेलोशिप','NGOs & volunteering':'एनजीओ और स्वयंसेवा','Startup funding':'स्टार्टअप फंडिंग','Student founders':'छात्र संस्थापक','Scholarships & grants':'छात्रवृत्ति और अनुदान','Schools & colleges':'स्कूल और कॉलेज','Jobs, events & hackathons':'नौकरियाँ, कार्यक्रम और हैकाथॉन','Export CSV':'CSV डाउनलोड करें','Download CSV':'CSV डाउनलोड करें','Build dataset':'डेटासेट बनाएं','Search':'खोजें','Search packs':'डेटा पैक खोजें','Close':'बंद करें','Sources':'स्रोत','Source':'स्रोत','Status':'स्थिति','Location':'स्थान','Eligibility':'पात्रता','Deadline':'अंतिम तिथि','Type':'प्रकार','All':'सभी','Research':'शोध','Opportunities':'अवसर','Review':'समीक्षा','Save dataset':'डेटासेट सहेजें','Institution database':'संस्थान डेटाबेस','Live maps':'लाइव मानचित्र','Upload data':'डेटा अपलोड करें','Source evidence':'स्रोत प्रमाण','Not provided by source':'स्रोत में उपलब्ध नहीं','Organisation':'संगठन','Amount':'राशि','Round':'फंडिंग चरण','Announcement date':'घोषणा की तिथि'
};
const lookup=new Map(Object.entries(labels).map(([k,v])=>[k.toLowerCase(),v]));
const originals=new WeakMap();
export function translateUI(root=document){
 const hindi=document.documentElement.lang==='hi';
 root.querySelectorAll('button,th,label,h1,h2,h3,h4,.pack-cluster span,[role="tab"],.missing-value').forEach(el=>{
  if(el.closest('[data-i],blockquote,pre,code,#language'))return;
  for(const node of el.childNodes){
   if(node.nodeType!==Node.TEXT_NODE)continue;
   const current=node.textContent;let saved=originals.get(node);
   if(saved&&current!==saved.en&&current!==saved.hi)saved=null;
   if(!saved){const value=lookup.get(current.trim().replaceAll('_',' ').toLowerCase());if(!value)continue;saved={en:current,hi:current.replace(current.trim(),value)};originals.set(node,saved);}
   const next=hindi?saved.hi:saved.en;if(current!==next)node.textContent=next;
  }
 });
}
let queued=false;
new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;translateUI();});}).observe(document.body,{childList:true,subtree:true,characterData:true});
document.addEventListener('eklist:language',()=>translateUI());
translateUI();
