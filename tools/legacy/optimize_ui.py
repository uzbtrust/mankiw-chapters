from pathlib import Path
p=Path('/Users/uzbtrust/Documents/Codex/2026-10-13/sh-2/work/app.js')
s=p.read_text()
backup=p.with_name('app-before-optimization.js')
if not backup.exists():backup.write_text(s)
start=s.index('function renderChapter(');end=s.index('function watchSections(',start)
s=s[:start]+r'''
let navigationSerial=0,renderedChapter=null,modelPromise=null;
const chapterTemplates=new Map(),chapterRequests=new Map();
async function getChapterTemplate(c){
 const inline=document.getElementById(`template-${c.id}`);if(inline)return inline.content;
 if(chapterTemplates.has(c.id))return chapterTemplates.get(c.id);
 if(!chapterRequests.has(c.id)){const request=fetch(c.contentUrl).then(async r=>{if(!r.ok)throw new Error('Chapter unavailable');const t=document.createElement('template');t.innerHTML=await r.text();chapterTemplates.set(c.id,t.content);return t.content;}).catch(e=>{chapterRequests.delete(c.id);throw e;});chapterRequests.set(c.id,request);}
 return chapterRequests.get(c.id);
}
function ensureModels(){
 if(typeof mountSimulations==='function')return Promise.resolve();
 if(!modelPromise)modelPromise=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=SIM_SCRIPT_URL;script.onload=resolve;script.onerror=()=>{script.remove();modelPromise=null;reject(new Error('Model unavailable'));};document.head.append(script);});
 return modelPromise;
}
function attachModels(c){
 if(typeof mountSimulations==='function'){mountSimulations($('#chapter-content'));return;}
 const host=$('#chapter-content [data-interactive]');if(!host)return;
 const pending=document.createElement('p');pending.className='source-note model-pending';pending.textContent='Interaktiv model yuklanmoqda…';host.before(pending);
 ensureModels().then(()=>{pending.remove();if(activeChapter?.id===c.id&&renderedChapter===c.id)mountSimulations($('#chapter-content'));}).catch(()=>{if(!pending.isConnected)return;pending.textContent='Model yuklanmadi. Internet aloqasini tekshirib, qayta urinib ko‘ring. ';const b=document.createElement('button');b.type='button';b.className='quiet-button';b.textContent='Qayta yuklash';b.addEventListener('click',()=>{pending.remove();attachModels(c)});pending.append(b);});
}
function applyAnchor(anchor,same){
 if(anchor){const target=document.getElementById(anchor);if(target){if(presentation){slideIndex=activeSections.findIndex(s=>s.contains(target)||s===target);showSlide(Math.max(0,slideIndex));}target.closest('details')?.setAttribute('open','');requestAnimationFrame(()=>target.scrollIntoView({behavior:'auto',block:'start'}));}}
 else if(!same)window.scrollTo({top:0,behavior:'instant'});
 updateProgress();
}
async function renderChapter(id,anchor){
 const c=CHAPTERS.find(x=>x.id===id);if(!c){location.hash='bosh-sahifa';return;}
 const serial=++navigationSerial,same=activeChapter?.id===id&&renderedChapter===id;
 $('#landing').hidden=true;$('#reader').hidden=false;
 $$('[data-chapter]').forEach(a=>{a.classList.toggle('active',Number(a.dataset.chapter)===id);if(Number(a.dataset.chapter)===id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 storeLocal('econ-last',{chapter:id,section:anchor||''});lastLocation={chapter:id,section:anchor||''};
 if(same){applyAnchor(anchor,true);return;}
 exitPresentation();sectionObserver?.disconnect();activeChapter=c;renderedChapter=null;activeSections=[];allAnswers=false;$('#reading-progress').style.width='0';$('#answer-toggle').textContent='Yechimlarni ochish';$('#answer-toggle').disabled=true;$('#presentation-toggle').disabled=true;$('#print-button').disabled=true;
 $('#chapter-content').innerHTML='<p class="chapter-loading" role="status">Bob yuklanmoqda…</p>';$('#chapter-end').innerHTML='';
 $('#chapter-header').innerHTML=`<p class="eyebrow">${String(id).padStart(2,'0')}-BOB · IQTISODIYOT ASOSLARI</p><h1>${esc(c.title)}</h1><p class="english-title">${esc(c.englishTitle)}</p><p class="lead">${esc(c.lead)}</p><div class="chapter-facts"><span>Kitob: ${c.sourcePages[0]}–${c.sourcePages[1]}-sahifalar</span><span>${c.sections.length} tushuntirish bo‘limi</span><span>${c.totalAnswered} izohli javob</span></div>`;
 const toc=c.sections.map((s,i)=>`<a href="#bob-${id}/${s.id}" data-section="${s.id}">${String(i+1).padStart(2,'0')} · ${esc(s.title)}</a>`).join('');$('#toc-nav').innerHTML=toc;$('#inline-toc').innerHTML=`<details><summary>Bob mundarijasi · ${c.sections.length} bo‘lim</summary><div class="toc-items">${toc}</div></details>`;$('#reader-position').textContent=`${String(id).padStart(2,'0')} / 10`;
 document.title=`${c.title} · Iqtisodiyot`;$('#announcer').textContent=`${id}-bob: ${c.title}`;
 if(!anchor){const heading=$('#chapter-header h1');heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});}
 try{
  const template=await getChapterTemplate(c);if(serial!==navigationSerial||activeChapter?.id!==id)return;
  $('#chapter-content').replaceChildren(template.cloneNode(true));activeSections=$$('#chapter-content>.lesson-section');renderedChapter=id;
  $('#answer-toggle').disabled=false;$('#presentation-toggle').disabled=false;$('#print-button').disabled=false;
  $('#chapter-end').innerHTML=`<p class="end-note">Endi shu bobning asosiy g‘oyasini kitobga qaramay, o‘z so‘zingiz bilan tushuntirib ko‘ring.</p><button type="button" class="complete-button ${finished.includes(id)?'is-complete':''}" data-complete="${id}">${finished.includes(id)?'✓ Bob o‘qib chiqildi':'Bobni o‘qib chiqdim'}</button><div class="chapter-end-nav">${id>1?`<a href="#bob-${id-1}">← <span>${esc(CHAPTERS.find(c=>c.id===id-1).title)}</span></a>`:'<a href="#bosh-sahifa">← Boblar ro‘yxati</a>'}${id<10?`<a href="#bob-${id+1}"><span>${esc(CHAPTERS.find(c=>c.id===id+1).title)}</span> →</a>`:'<a href="#bosh-sahifa">Barcha boblar →</a>'}</div>`;
  attachModels(c);watchSections();applyAnchor(anchor,false);
 }catch{if(serial!==navigationSerial)return;$('#chapter-content').innerHTML='<div class="load-error" role="status"><h2>Bob yuklanmadi</h2><p>Internet aloqasi tiklangach, qayta urinib ko‘ring. Yuklangan boblar shu oynada saqlanadi.</p><button class="quiet-button" id="chapter-retry" type="button">Qayta yuklash</button></div>';$('#chapter-retry').addEventListener('click',()=>renderChapter(id,anchor));}
}
function route(){const h=decodeURIComponent(location.hash.slice(1));const m=h.match(/^bob-(\d+)(?:\/(.+))?$/);if(m){renderChapter(Number(m[1]),m[2]);return;}navigationSerial++;exitPresentation();sectionObserver?.disconnect();activeChapter=null;renderedChapter=null;activeSections=[];$('#landing').hidden=false;$('#reader').hidden=true;$('#reading-progress').style.width='0';renderDirectory();document.title='Iqtisodiyot · Tushunib o‘rganing';if(h==='boblar')requestAnimationFrame(()=>$('#boblar').scrollIntoView());else window.scrollTo({top:0,behavior:'instant'});}
''' +s[end:]
start=s.index('const searchIndex=');end=s.index('const searchDialog=',start)
s=s[:start]+r'''
let searchPromise=null,searchSerial=0,searchTimer=null;
async function getSearchIndex(){
 if(!searchPromise)searchPromise=(async()=>{
  let rows;
  if(COURSE_ONLINE){const r=await fetch(SEARCH_INDEX_URL);if(!r.ok)throw new Error('Search unavailable');rows=await r.json();}
  else rows=CHAPTERS.flatMap(c=>Array.from(document.getElementById(`template-${c.id}`).content.querySelectorAll('.lesson-section')).flatMap(s=>[{c:c.id,i:s.id,t:s.querySelector('h2')?.textContent||'',x:s.textContent.replace(/\s+/g,' ').trim()},...Array.from(s.querySelectorAll('details.answer[id]')).map(q=>({c:c.id,i:q.id,t:q.querySelector('summary')?.textContent||'',x:q.textContent.replace(/\s+/g,' ').trim(),q:true}))]));
  return rows.map(r=>{const chapter=CHAPTERS.find(c=>c.id===r.c);return{chapter,id:r.i,title:r.t,text:r.x,question:!!r.q,nt:norm(r.t),nx:norm(r.x),nc:norm(chapter.title)}});
 })().catch(e=>{searchPromise=null;throw e;});
 return searchPromise;
}
async function search(){
 const serial=++searchSerial,raw=$('#search-input').value.trim(),q=norm(raw);if(q.length<2){$('#search-status').textContent='Kamida ikki harf yozing. Atama, savol yoki misolni qidirishingiz mumkin.';$('#search-results').innerHTML='';return;}
 $('#search-status').textContent='Qidirilmoqda…';
 try{const index=await getSearchIndex();if(serial!==searchSerial||norm($('#search-input').value.trim())!==q)return;
 const hits=index.map(s=>({...s,score:s.nt.includes(q)?(s.question?4:3):s.nc.includes(q)?2:s.nx.includes(q)?1:0})).filter(s=>s.score).sort((a,b)=>b.score-a.score).slice(0,18);
 $('#search-status').textContent=hits.length?`${hits.length} mos bo‘lim topildi. Natijani bosib, bobga o‘ting.`:'Mos bo‘lim topilmadi. Boshqa atama yoki qisqaroq so‘z bilan sinab ko‘ring.';$('#search-results').innerHTML=hits.map(s=>{const pos=s.nx.indexOf(q),start=Math.max(0,pos-75),snip=s.text.slice(start,start+210);return `<a class="search-result" href="#bob-${s.chapter.id}/${s.id}"><small>${String(s.chapter.id).padStart(2,'0')}-BOB · ${esc(s.chapter.title)}</small><strong>${esc(s.title)}</strong><p>${start?'…':''}${esc(snip)}…</p></a>`}).join('');
 }catch{if(serial===searchSerial){$('#search-status').textContent='Qidiruv ma’lumoti yuklanmadi. Internet aloqasi tiklangach, so‘zni qayta yozib ko‘ring.';$('#search-results').innerHTML='';}}
}
''' +s[end:]
s=s.replace("$('#search-input').addEventListener('input',search)","$('#search-input').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(search,160)})")
p.write_text(s)
sim=p.with_name('simulations.js');v=sim.read_text();v=v.replace("const type=h.dataset.interactive;","if(h.dataset.mounted==='true')return;h.dataset.mounted='true';const type=h.dataset.interactive;");sim.write_text(v)
css=p.with_name('style.css');v=css.read_text();v+='\n.chapter-loading,.load-error{padding:45px 0;color:var(--muted);font-size:16px}.load-error h2{font:400 30px var(--serif);color:var(--ink)}.load-error p{margin:18px 0}\n';css.write_text(v)
print('Runtime now loads chapter content, models and full-text search on demand')
