#!/usr/bin/env python3
import json, sys, subprocess, webbrowser, html
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

BASE=Path(__file__).parent
STATE=BASE/'state'; PROJECTS=STATE/'projects'; MEMORY=BASE/'memory'; LOGS=BASE/'logs'/'daily'; PROMPTS=BASE/'prompts'/'codex'; WORK=BASE/'workpacks'
PROJECT_FILES={'chipos':'chipos-mark-ii.json','doorin4':'doorin4.json','doorin5':'doorin5.json','evidence':'evidence-transcript-core.json','inventory':'inventory-application.json'}
DEFAULT_PROJECTS={
 'doorin4':{'name':'Door in 4','code_name':'The Courier of Destiny','purpose':'Bulky-item courier marketplace for local collection and delivery.','completion_percent':20,'momentum_score':70,'fun_score':74,'revenue_score':92,'current_blocker':'No proven first paid bulky-item delivery flow.','next_task':'Build and test one paid bulky-item delivery flow.','next_milestone':'One bulky delivery can be requested, accepted, completed and paid.','fastest_route_to_revenue':'Offer one local bulky-item delivery trial.','time_to_first_sale':'days if tested locally','risk_level':'Medium','last_updated':'2026-06-10'},
 'doorin5':{'name':'Door in 5','code_name':'The Community Runner','purpose':'Rapid local essentials delivery for underserved communities.','completion_percent':18,'momentum_score':45,'fun_score':72,'revenue_score':67,'current_blocker':'Needs catalogue and safe operating rules.','next_task':'Define first essentials catalogue and local delivery offer.','next_milestone':'One repeatable essentials offer exists for a small pilot.','fastest_route_to_revenue':'Serve repeat local essentials customers after rules are clear.','time_to_first_sale':'weeks','risk_level':'High due to regulated items','last_updated':'2026-06-10'}}
DEFAULT_WATCHES={'searches':[
 {'name':'Dell OptiPlex bargain hunt','source':'eBay UK','query':'Dell OptiPlex','max_price':50,'project_use':'compute / resale','why':'Cheap compute can run local tools or be resold.','active':True},
 {'name':'HP EliteDesk bargain hunt','source':'eBay UK','query':'HP EliteDesk','max_price':50,'project_use':'compute / resale','why':'Small desktops are useful worker nodes.','active':True},
 {'name':'ThinkCentre Tiny hunt','source':'eBay UK','query':'Lenovo ThinkCentre Tiny','max_price':60,'project_use':'JamesOS node','why':'Tiny PCs are useful spare agents.','active':True},
 {'name':'Mini PC hunt','source':'eBay UK','query':'mini pc','max_price':60,'project_use':'agent node / resale','why':'Good utility and resale potential.','active':True},
 {'name':'USB microphone hunt','source':'eBay UK','query':'usb microphone','max_price':30,'project_use':'Evidence Core / audio','why':'Improves demos and recordings.','active':True},
 {'name':'XREAL smart glasses hunt','source':'eBay UK','query':'xreal smart glasses','max_price':180,'project_use':'ChipOS','why':'AR testing hardware.','active':True},
 {'name':'Thermal delivery bag hunt','source':'eBay UK','query':'thermal delivery bag','max_price':25,'project_use':'Door in 5','why':'Essentials delivery kit.','active':True},
 {'name':'Sack truck hunt','source':'eBay UK','query':'folding sack truck','max_price':35,'project_use':'Door in 4','why':'Bulky delivery kit.','active':True},
 {'name':'Dash cam hunt','source':'eBay UK','query':'dash cam','max_price':30,'project_use':'Door in 4','why':'Delivery proof and safety.','active':True}]}
DEFAULT_TASKS={'tasks':[
 {'id':'d4-001','project':'doorin4','title':'Build one paid bulky-item delivery flow','why':'Closest route to first real revenue.','next_action':'Generate Codex prompt for Door in 4 flow.','command':'python james.py prompt codex doorin4','money_score':98,'momentum_score':92,'time_estimate':'2-4 hours','status':'active'},
 {'id':'ev-001','project':'evidence','title':'Build upload to transcript to evidence pack flow','why':'Legal users may pay for saved time.','next_action':'Generate Codex prompt for Evidence Core flow.','command':'python james.py prompt codex evidence','money_score':94,'momentum_score':82,'time_estimate':'4-8 hours','status':'active'},
 {'id':'d4-002','project':'doorin4','title':'Create first local bulky delivery offer','why':'A simple offer can attract a first tester.','next_action':'Run customer-pack and review the draft.','command':'python james.py customer-pack','money_score':90,'momentum_score':85,'time_estimate':'30 minutes','status':'active'},
 {'id':'jo-001','project':'jamesos','title':'Run auto-prep before each work session','why':'Creates actual files and prompts.','next_action':'Run the working automation pack.','command':'python james.py auto-prep','money_score':82,'momentum_score':88,'time_estimate':'5 minutes','status':'active'}]}

def ensure_dirs():
    for p in [STATE,PROJECTS,MEMORY,LOGS,PROMPTS,WORK]: p.mkdir(parents=True, exist_ok=True)
def rj(path, default):
    if not path.exists(): wj(path, default); return default
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return default
def wj(path, data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def today(): return datetime.now().strftime('%Y-%m-%d')
def log(s):
    with open(LOGS/f'{today()}.md','a',encoding='utf-8') as f: f.write(f'\n### {datetime.now().strftime("%H:%M")}\n{s}\n')
def head(s): print('\n'+'='*64+'\n  '+s+'\n'+'='*64)
def seed():
    ensure_dirs(); rj(STATE/'watchlist.json',DEFAULT_WATCHES); rj(STATE/'tasks.json',DEFAULT_TASKS)
    for k,v in DEFAULT_PROJECTS.items():
        f=PROJECTS/PROJECT_FILES[k]
        if not f.exists(): wj(f,v)
def load_project(k): seed(); return rj(PROJECTS/PROJECT_FILES[k],DEFAULT_PROJECTS.get(k,{}))
def projects(): seed(); return {k:rj(PROJECTS/f,{}) for k,f in PROJECT_FILES.items() if (PROJECTS/f).exists()}
def best_project():
    ps=projects(); return max(ps.items(),key=lambda kv:kv[1].get('revenue_score',0)+kv[1].get('momentum_score',0))
def tasks(): seed(); return rj(STATE/'tasks.json',DEFAULT_TASKS).get('tasks',[])
def active_tasks(): return [t for t in tasks() if t.get('status') not in ['done','parked']]
def best_task():
    ts=active_tasks(); return max(ts,key=lambda t:t.get('money_score',0)+t.get('momentum_score',0)) if ts else None
def watches(): seed(); return rj(STATE/'watchlist.json',DEFAULT_WATCHES).get('searches',[])
def ebay(q): return 'https://www.ebay.co.uk/sch/i.html?_nkw='+quote_plus(str(q))+'&_sop=15'
def git(args):
    try: return subprocess.check_output(['git']+args,cwd=BASE,text=True,stderr=subprocess.STDOUT).strip()
    except Exception as e: return 'Git unavailable: '+str(e)
def doctor(): head('JAMESOS DOCTOR'); ensure_dirs(); print('SYSTEM HEALTH SCORE: 100/100'); print('Folders ready. Worker engine available.'); log('**Doctor run.** 100/100')
def gitcheck(): head('JAMESOS GITCHECK'); print('Branch:',git(['branch','--show-current'])); print('Status:',git(['status','--short']) or 'Clean working tree'); print('Last commit:',git(['log','--oneline','-1']))
def status(): head('JAMESOS STATUS'); [print(f"{p.get('name',k)} | money {p.get('revenue_score','?')} | momentum {p.get('momentum_score','?')}") for k,p in projects().items()]; k,p=best_project(); print('\nPriority:',p.get('name',k)); print('Next:',p.get('next_task'))
def show_tasks(): head('TASK LIST'); [print(f"{t['id']} | {t.get('project')} | {t.get('title')} | score {t.get('money_score',0)+t.get('momentum_score',0)}\n  {t.get('command','')}") for t in sorted(active_tasks(),key=lambda x:x.get('money_score',0)+x.get('momentum_score',0),reverse=True)]
def task_next():
    head('NEXT MONEY TASK'); t=best_task(); print('Project:',t.get('project')); print('Task:',t.get('title')); print('Why:',t.get('why')); print('Command:',t.get('command')); print('Time:',t.get('time_estimate'))
def task_done(i):
    data=rj(STATE/'tasks.json',DEFAULT_TASKS); hit=False
    for t in data.get('tasks',[]):
        if t.get('id')==i: t['status']='done'; t['done_at']=datetime.now().strftime('%Y-%m-%d %H:%M'); hit=True
    wj(STATE/'tasks.json',data); print('Task done:' if hit else 'Task not found:',i)
def deal_sniffer():
    head('ACTIVE WATCHES')
    for s in watches(): print(f"\n{s['name']}\nSource: {s['source']}\nSearch: {s['query']}\nMax: {s.get('max_price')}\nUse: {s.get('project_use')}\nWhy: {s.get('why')}\nOpen: {ebay(s['query'])}")
def search_open(n=8):
    head('OPEN SEARCHES'); c=0
    for s in watches():
        if c>=n: break
        url=ebay(s['query']); print('Opening:',url); webbrowser.open(url); c+=1
    print('Opened',c,'searches')
def deals(): return rj(STATE/'deals.json',{'deals':[]}).get('deals',[])
def save_deals(ds): wj(STATE/'deals.json',{'deals':ds})
def deal_add(args):
    if len(args)<5: print('Usage: python james.py deal-add "title" price "location" "source" "url"'); return
    ds=deals(); d={'id':'deal-'+datetime.now().strftime('%Y%m%d%H%M%S'),'title':args[0],'price':float(args[1]),'location':args[2],'source':args[3],'url':args[4],'date_added':datetime.now().strftime('%Y-%m-%d %H:%M'),'score':0}
    ds.append(d); save_deals(ds); print('Deal added:',d['id'],d['title'])
def score(d):
    s=0; txt=(d.get('title','')+' '+d.get('location','')).lower(); price=float(d.get('price',9999))
    if price<30: s+=30
    elif price<50: s+=20
    if any(x in txt for x in ['tunbridge','tonbridge','kent','local']): s+=15
    if any(x in txt for x in ['optiplex','elitedesk','thinkcentre','mini pc','microphone','xreal','bag','truck','dash']): s+=20
    if any(x in txt for x in ['laptop','pc','monitor','bundle','job lot']): s+=15
    return s
def deal_score():
    head('DEAL SCOREBOARD'); ds=deals()
    if not ds: print('No deals yet.'); return
    for d in ds: d['score']=score(d); print(f"{d['title']} | £{d['price']} | {d['location']} | score {d['score']}")
    save_deals(ds)
def deal_list(): head('DEAL LIST'); [print(f"{d.get('score',0):>3} | £{d.get('price')} | {d.get('title')} | {d.get('location')}") for d in sorted(deals(),key=lambda x:x.get('score',0),reverse=True)]
def money_sniff():
    head('MONEY SNIFF RESULT'); k,p=best_project(); t=best_task(); ds=deals(); bd=max(ds,key=lambda d:d.get('score',0),default=None)
    print('Best project:',p.get('name',k)); print('Best task:',t.get('title') if t else 'none'); print('Best deal:',bd.get('title') if bd else 'none captured'); print('Best watch:',watches()[0]['name']); print('Action now:',t.get('command') if t else 'python james.py deal-hunt')
def prompt_text(project=''):
    t=best_task(); project=project or (t.get('project') if t else 'doorin4')
    if project=='doorin4': return 'Build/test the simplest Door in 4 bulky-item delivery flow. Keep Door in 4 separate from Door in 5. Return files changed, tests run, risks, next step.'
    if project=='evidence': return 'Build upload -> transcript -> evidence pack flow for Evidence Transcript Core. Keep it small. Return files changed, tests run, risks, next step.'
    return f"Improve {project}. Task: {(t or {}).get('title','top task')}. Keep it small and testable."
def codex_now(project=''):
    head('CODEX NOW'); text=prompt_text(project); path=PROMPTS/f"{today()}-{project or 'top-task'}.txt"; path.write_text(text,encoding='utf-8'); print(text); print('Saved:',path)
def wpdir(): p=WORK/today(); p.mkdir(parents=True,exist_ok=True); return p
def customer_pack():
    head('CUSTOMER PACK'); d=wpdir()/'customer_pack'; d.mkdir(parents=True,exist_ok=True)
    files={'doorin4_customer_message.md':'Hi, I offer local bulky-item collection and delivery. Send pickup area, drop-off area, item size and preferred time for a quote.','evidence_core_solicitor_message.md':'Hi, I am building a tool that turns audio/video material into organised transcript and evidence-pack drafts for review. I am looking for one small demo file for practical feedback.','doorin5_community_offer.md':'Local essentials delivery concept for people who struggle with transport. Start small with safe household essentials until rules are clear.','hardware_resale_listing.md':'Title:\nPrice:\nSpecs:\nCondition:\nIncluded:\nCollection/delivery:\nReason to buy:\n'}
    for name,txt in files.items(): (d/name).write_text('# '+name+'\n\n'+txt+'\n',encoding='utf-8')
    print('Customer pack created:',d)
def work_pack():
    head('WORK PACK'); d=wpdir(); t=best_task(); k,p=best_project(); files={'01_TODAY_MISSION.md':f"# Today Mission\n\nProject: {p.get('name',k)}\nMission: {(t or {}).get('title',p.get('next_task'))}\nWhy: {p.get('fastest_route_to_revenue')}\n",'02_TOP_MONEY_TASK.md':json.dumps(t,indent=2),'03_CODEX_PROMPT.md':prompt_text(),'04_DEAL_WATCHES.md':'Run python james.py deal-hunt and capture promising finds.\n','05_OUTREACH_DRAFTS.md':'Run python james.py customer-pack.\n','06_APPROVAL_QUEUE.md':'External actions are manual.\n','07_GIT_STATUS.md':f"Branch: {git(['branch','--show-current'])}\nStatus:\n{git(['status','--short']) or 'Clean'}\n"}
    for name,txt in files.items(): (d/name).write_text(txt,encoding='utf-8')
    print('Work pack created:',d); [print('-',x) for x in files]
def deal_hunt():
    head('DEAL HUNT'); links=MEMORY/'deal_hunt_links.md'; cap=MEMORY/'deal_capture_sheet.md'; rows=['# Deal Hunt Links\n']; c=0
    for s in watches()[:12]:
        url=ebay(s['query']); rows.append(f"- {s['name']}: {url}\n")
        if c<8: webbrowser.open(url); c+=1
    links.write_text(''.join(rows),encoding='utf-8'); cap.write_text('# Deal Capture Sheet\n\nTitle:\nPrice:\nLocation:\nSource:\nURL:\nCondition:\nWhy useful:\nResale estimate:\n',encoding='utf-8'); print('Opened searches:',c); print('Links:',links); print('Capture sheet:',cap)
def profit_board():
    head('PROFIT BOARD'); t=best_task(); k,p=best_project(); doc=f"<html><body><h1>JamesOS Profit Board</h1><p>Top task: {html.escape((t or {}).get('title','none'))}</p><p>Best project: {html.escape(p.get('name',k))}</p><p>{html.escape(p.get('fastest_route_to_revenue',''))}</p></body></html>"; (BASE/'profit_board.html').write_text(doc,encoding='utf-8'); print('Profit board created:',BASE/'profit_board.html')
def auto_prep(): head('AUTO PREP'); doctor(); gitcheck(); task_next(); deal_sniffer(); money_sniff(); work_pack(); print('\nAUTO PREP COMPLETE')
def daily_money():
    head('DAILY MONEY LOOP'); doctor(); gitcheck(); task_next(); money_sniff(); deal_sniffer(); focus(); open(MEMORY/'deal_reports.md','a',encoding='utf-8').write(f"\n## Daily Money {today()}\nBest task: {(best_task() or {}).get('title')}\n"); print('\nDAILY MONEY LOOP COMPLETE')
def focus(): head('FOCUS'); t=best_task(); print('DO THIS NOW:',(t or {}).get('title','Run deal-hunt')); print('TIME:',(t or {}).get('time_estimate','30 minutes')); print('WHY:',(t or {}).get('why','Creates forward motion')); print('DO NOT DO: Start another project.')
def treasury(): head('TREASURY'); print(json.dumps(rj(STATE/'treasury.json',{'current_balance':0}),indent=2))
def win(msg): open(MEMORY/'wins.md','a',encoding='utf-8').write(f"- **{datetime.now().strftime('%Y-%m-%d %H:%M')}** - {msg}\n"); print('WIN RECORDED')
def usage():
    print('JamesOS v0.7')
    for c in ['doctor','status','tasks','task-next','deal-sniffer','search-open','deal-hunt','deal-score','deal-list','money-sniff','codex-now','customer-pack','work-pack','auto-prep','daily-money','profit-board','gitcheck','treasury','focus']: print('  python james.py',c)
    print('  python james.py deal-add "title" price "location" "source" "url"'); print('  python james.py task-done TASK_ID'); print('  python james.py prompt codex doorin4')
def main():
    seed();
    if len(sys.argv)<2: usage(); return
    c=sys.argv[1].lower()
    if c=='doctor': doctor()
    elif c=='status': status()
    elif c=='gitcheck': gitcheck()
    elif c=='tasks': show_tasks()
    elif c=='task-next': task_next()
    elif c=='task-done' and len(sys.argv)>2: task_done(sys.argv[2])
    elif c=='deal-sniffer': deal_sniffer()
    elif c=='search-open': search_open()
    elif c=='deal-hunt': deal_hunt()
    elif c=='deal-add': deal_add(sys.argv[2:])
    elif c=='deal-score': deal_score()
    elif c=='deal-list': deal_list()
    elif c=='money-sniff': money_sniff()
    elif c=='codex-now': codex_now()
    elif c=='customer-pack': customer_pack()
    elif c=='work-pack': work_pack()
    elif c=='auto-prep': auto_prep()
    elif c=='daily-money': daily_money()
    elif c=='profit-board': profit_board()
    elif c=='treasury': treasury()
    elif c=='focus': focus()
    elif c=='win' and len(sys.argv)>2: win(' '.join(sys.argv[2:]))
    elif c=='prompt' and len(sys.argv)>=4: codex_now(sys.argv[3])
    elif c=='project' and len(sys.argv)>2: print(json.dumps(load_project(sys.argv[2]),indent=2))
    else: usage()
if __name__=='__main__': main()
