/* Library-owned Appian semantic recorder. No external scripts or assets. */
(() => {
  if (window.__roboRecorderInstalled) return;
  window.__roboRecorderInstalled = true;
  let enabled = false, verifying = false, lookup = null, menu = [], host, shadow;
  const dirty = new WeakSet();
  const active = () => enabled || window !== window.top; // Host enforces the recording gate for iframe events.
  const sensitive = el => !!el && (el.type === 'password' || ['username','current-password','new-password','one-time-code'].includes(el.autocomplete) || /^(un|pw)$/.test(el.id || '') || /password|user.?name|secret|token|credential|ssn/i.test([el.name,el.getAttribute('aria-label'),el.getAttribute('placeholder')].join(' ')));
  const norm = value => String(value || '').replace(/\s+/g, ' ').trim().replace(/\s*\*$/, '');
  const visible = el => !!(el && el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden');
  const text = el => norm(el && (el.innerText || el.textContent));
  const own = event => event.composedPath().includes(host);
  const fieldLabel = el => {
    const ids = (el.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean);
    if (ids.length) return norm(ids.map(id => document.getElementById(id)?.textContent || '').join(' '));
    if (el.getAttribute('aria-label')) return norm(el.getAttribute('aria-label'));
    if (el.labels?.length) return text(el.labels[0]);
    return text(Array.from(document.querySelectorAll('label')).find(l => l.htmlFor && l.htmlFor === el.id));
  };
  const name = el => fieldLabel(el) || norm(el.getAttribute('title')) || text(el) || norm(el.value);
  const controls = () => Array.from(document.querySelectorAll('input,textarea,select,[role="combobox"],button,a,[role="tab"],[role="button"]')).filter(visible);
  function identify(el) {
    if (!el || sensitive(el)) return null;
    if ((el.tagName==='INPUT'&&['file','range','color','submit','button','reset','hidden'].includes(el.type)) || (el.tagName!=='INPUT'&&el.matches('[role="checkbox"],[role="radio"]'))) return {component:'unsupported',name:fieldLabel(el)||el.type||el.getAttribute('role')};
    const role = el.getAttribute('role'), tag = el.tagName;
    let target;
    if (el.matches('input[type="checkbox"],[role="checkbox"]')) target = {component:'checkbox',label:fieldLabel(el)};
    else if (el.matches('input[type="radio"],[role="radio"]')) {
      const group = el.closest('[role="radiogroup"],fieldset');
      target = {component:'radio',label:group ? fieldLabel(group) || text(group.querySelector('legend')) : ''};
    } else if (el.matches('input,textarea')) {
      target = {component:el.type === 'date' || (el.getAttribute('data-testid') || '').includes('DatePicker') ? 'date':'textbox'};
      if (fieldLabel(el)) target.label = fieldLabel(el);
      else if (el.getAttribute('placeholder')) target.placeholder = el.getAttribute('placeholder');
    } else if (role === 'combobox' || tag === 'SELECT') target = {component:'dropdown',label:fieldLabel(el)};
    else if (role === 'tab' || (tag === 'A' && /Selected Tab\.|Unselected Tab\./.test(el.textContent))) {
      target = {component:'tab',name:norm(text(el).replace(/(?:Unselected|Selected) Tab\..*$/, ''))};
    } else if ((tag === 'BUTTON' || role === 'button') && el.getAttribute('aria-haspopup') && !['listbox','false'].includes(el.getAttribute('aria-haspopup'))) target = {component:'menu',path:[name(el)]};
    else if (tag === 'BUTTON' || role === 'button') target = {component:'button',name:name(el)};
    else if (tag === 'A') target = {component:'link',name:name(el)};
    else return null;
    const dialog = el.closest('[role="dialog"]');
    if (dialog) target.dialog = fieldLabel(dialog) || text(dialog.querySelector('h1,h2,h3'));
    if (el.closest('td')) target.ambiguous = true; // Editable grid mappings must be reviewed explicitly.
    const identifier = target.label || target.placeholder || target.name;
    if (identifier && !['radio','menu'].includes(target.component)) {
      const scope = dialog || document;
      const duplicates = controls().filter(other => scope.contains(other) && (
        target.label ? fieldLabel(other) === identifier : target.placeholder ? other.getAttribute('placeholder') === identifier : name(other) === identifier
      ) && (['textbox','date'].includes(target.component) ? other.matches('input,textarea') : target.component==='dropdown' ? other.matches('select,[role="combobox"]') : target.component==='button' ? other.matches('button,[role="button"]') : target.component==='link' ? other.tagName==='A' : true));
      target.ambiguous = target.ambiguous || duplicates.length > 1;
    }
    if (tag === 'SELECT') target.native_select = true;
    return target;
  }
  function gridTarget(el) {
    const cell = el.closest('td'), table = cell?.closest('table');
    if (!cell || !table) return null;
    let header = fieldLabel(table);
    if (!header) {
      const region = table.closest('[role="region"],section');
      header = region && (fieldLabel(region) || text(region.querySelector('h1,h2,h3,h4')));
    }
    const row = cell.closest('tr');
    const rows = Array.from(table.querySelectorAll('tbody tr')).filter(r=>r.querySelector('td'));
    const headers = Array.from(table.querySelectorAll('thead tr')).at(-1)?.querySelectorAll('th,td');
    return {component:'grid_cell',grid:{header:header || '',row_number:rows.indexOf(row)+1,column_name:headers ? text(headers[cell.cellIndex]):''}};
  }
  function emit(action,target,value='',extra={}) {
    if (!target) return;
    const payload = {action,target,value,...extra};
    if (target.native_select) payload.blocker = 'Native select needs a generic web adapter; RoboAppian dropdown expects an Appian combobox.';
    window.__roboRecorderBridge({command:'event',payload}).then(update).catch(showError);
  }
  function update(result) {
    if (!result) return;
    enabled = result.recording; verifying = result.verifying;
    if (!shadow) return;
    shadow.querySelector('#status').textContent = enabled ? (verifying ? 'VERIFY · click a field or outcome':'RECORDING · perform your workflow') : 'PAUSED · sign in and choose a stable entry page';
    shadow.querySelector('#toggle').textContent = enabled ? 'Pause':'Start recording';
    shadow.querySelector('#verify').textContent = verifying ? 'Cancel verify':'Add verification';
    shadow.querySelector('#count').textContent = result.steps.length + ' steps · ' + result.issues.length + ' export issue(s)';
    if (shadow.querySelector('#review').open) renderReview(result);
    if (result.inspection) {
      const inventory=shadow.querySelector('#inventory');inventory.textContent='';
      for (const target of result.inspection) {
        const item=document.createElement('div');item.textContent=JSON.stringify(target);inventory.append(item);
      }
    }
  }
  function showError(error) { if(shadow) shadow.querySelector('#error').textContent=String(error.message || error); }
  function command(command,extra={}) { return window.__roboRecorderBridge({command,...extra}).then(result=>{shadow.querySelector('#error').textContent='';update(result);return result;}).catch(showError); }
  function renderReview(result) {
    const list=shadow.querySelector('#steps');list.textContent='';
    for (const step of result.steps) {
      const box=document.createElement('div');box.className='step';
      const title=document.createElement('b');title.textContent=step.id+' · '+step.action+' · '+(step.target.label||step.target.name||step.target.path?.join(' → ')||step.target.component);box.append(title);
      const mapping=document.createElement('div');mapping.className='muted';mapping.textContent=JSON.stringify(step.target);box.append(mapping);
      const input=document.createElement('input');input.value=step.value;input.setAttribute('aria-label','Expected value or input for '+step.id);input.disabled=!['fill','select','assert_value','assert_text'].includes(step.action);box.append(input);
      const approve=document.createElement('button');approve.textContent=step.approved?'Revoke approval':'Approve this step';approve.onclick=()=>command('review',{id:step.id,approve:!step.approved,value:input.value});box.append(approve);
      const remove=document.createElement('button');remove.textContent='Remove';remove.onclick=()=>command('remove',{id:step.id});box.append(remove);
      if(step.problems.length){const p=document.createElement('div');p.className='error';p.textContent=step.problems.join(' ');box.append(p);}
      list.append(box);
    }
  }
  function install() {
    if (!document.body || window !== window.top) return;
    host=document.createElement('div');host.id='robo-recorder-panel';document.documentElement.append(host);
    shadow=host.attachShadow({mode:'closed'});
    shadow.innerHTML=`<style>:host{all:initial;position:fixed;z-index:2147483647;top:12px;right:12px;width:350px;color:#17352f;font:12px/1.45 system-ui,sans-serif}*{box-sizing:border-box}.panel{background:#f7fcfa;border:1px solid #8bbaad;border-radius:12px;box-shadow:0 8px 30px #0003;padding:15px;max-height:88vh;overflow:auto}h3{margin:0 0 9px;font-size:17px}button{border:1px solid #b3cec4;border-radius:6px;background:white;padding:6px 8px;margin:4px 4px 3px 0;color:#135349;cursor:pointer}button.primary{background:#087e73;color:white}input{width:100%;padding:7px;border:1px solid #b3cec4;border-radius:5px;margin:6px 0}summary{cursor:pointer;margin:9px 0}.muted{color:#627770;font-size:10px;overflow-wrap:anywhere}.step{border-top:1px solid #d4e5dc;padding:10px 0}.error{color:#9a3c29;font-size:11px}#inventory{max-height:200px;overflow:auto;font:10px monospace;overflow-wrap:anywhere}#status{padding:8px;background:#e1f0e8;border-radius:6px;margin-bottom:7px}#count{margin:6px 0}small{display:block;color:#627770}</style><div class="panel"><h3>RoboAppian Recorder</h3><div id="status">Connecting…</div><button id="toggle" class="primary">Start recording</button><button id="verify">Add verification</button><button id="inspect">Inspect page</button><button id="save">Save draft</button><div id="count"></div><details id="review"><summary>Review steps & expected results</summary><small>Values are observations. Approve only when they match the intended business behavior. Editing requires approval again.</small><div id="steps"></div></details><details><summary>Semantic page inventory</summary><div id="inventory"></div></details><button id="finish">Save & finish</button><small>Recording starts paused. Credentials are excluded. This v1 supports one main page; ambiguous targets block export.</small><div id="error" class="error" role="status"></div></div>`;
    shadow.querySelector('#toggle').onclick=()=>command('toggle');
    shadow.querySelector('#verify').onclick=()=>command('verify');
    shadow.querySelector('#inspect').onclick=()=>command('inspect',{inspection:window.__roboRecorderInspect()});
    shadow.querySelector('#save').onclick=()=>command('save');
    shadow.querySelector('#finish').onclick=()=>command('finish');
    shadow.querySelector('#review').ontoggle=()=>{if(shadow.querySelector('#review').open)command('state');};
    command('state');
  }
  window.__roboRecorderInspect = () => controls().filter(el=>!sensitive(el)).map(identify).filter(Boolean).map(t=>({...t,observed:true})).slice(0,500);
  document.addEventListener('input',event=>{if(active()&&!own(event)&&!sensitive(event.target))dirty.add(event.target);},true);
  document.addEventListener('change',event=>{
    if(!active()||verifying||own(event)||sensitive(event.target))return;
    const el=event.target,target=identify(el);if(!target)return;
    if(target.component==='unsupported')emit('unsupported',target,'',{blocker:'This control needs a dedicated translation adapter.'});
    else if(target.component==='checkbox')emit(el.checked?'check':'uncheck',target);
    else if(target.component==='radio')emit('select',target,fieldLabel(el)||norm(el.value));
    else if(target.component==='dropdown')emit('select',target,text(el.selectedOptions?.[0]));
    else if(['textbox','date'].includes(target.component)){emit('fill',target,el.value);dirty.delete(el);}
  },true);
  document.addEventListener('focusout',event=>{
    if(!active()||verifying||own(event)||sensitive(event.target))return;
    const el=event.target,target=identify(el);
    if(target&&dirty.has(el)&&['textbox','date'].includes(target.component)){emit('fill',target,el.value);dirty.delete(el);}
  },true);
  document.addEventListener('click',event=>{
    if(own(event)||!active())return;
    let el=event.target instanceof Element ? event.target:null;if(!el||sensitive(el))return;
    if(verifying){
      event.preventDefault();event.stopImmediatePropagation();
      const control=el.closest('input,textarea,select,[role="combobox"],button,a,[role="button"]');
      const target=identify(control);
      if(target&&['textbox','date','dropdown'].includes(target.component)){
        const value=target.component==='dropdown'?(control.tagName==='SELECT'?text(control.selectedOptions?.[0]):text(control)):control.value;
        emit('assert_value',target,value);
      }else if(target&&['button','link'].includes(target.component))emit('assert_visible',target);
      else if(el.closest('td'))emit('assert_text',gridTarget(el),text(el.closest('td')));
      else {const value=text(el),matches=Array.from(document.querySelectorAll('body *')).filter(n=>!n.children.length&&visible(n)&&text(n)===value);emit('assert_visible',{component:'text',name:value,ambiguous:matches.length>1},'',value.length>300?{blocker:'Choose a smaller text outcome.'}:{});}
      verifying=false;command('verify_off');return;
    }
    const option=el.closest('[role="option"]');
    if(option&&lookup){emit('select',lookup.target,text(option),lookup.target.component==='textbox'?{search_text:lookup.input.value}:{});lookup=null;return;}
    const control=el.closest('input,textarea,select,[role="combobox"],button,a,[role="tab"],[role="button"],[role="menuitem"],[role="checkbox"],[role="radio"]');
    if(!control)return;
    const list=control.closest('[role="menu"],[role="dialog"]');
    if(menu.length&&list){const leaf=name(control);if(leaf)emit('click',{component:'menu',path:[...menu,leaf]});menu=[];return;}
    const target=identify(control);if(!target)return;
    if(target.component==='unsupported'){emit('unsupported',target,'',{blocker:'This control needs a dedicated translation adapter.'});return;}
    if(target.component==='menu'){menu=target.path;emit('open',target);return;}
    if(control.getAttribute('role')==='combobox'||(target.component==='textbox'&&control.getAttribute('aria-controls'))){lookup={target,input:control};return;}
    if(['button','link'].includes(target.component))emit('click',target,'',control.getAttribute('target')==='_blank'?{blocker:'Popup page switching requires a dedicated adapter.'}:{});
    else if(target.component==='tab')emit('select',target);
    else if(target.component==='textbox'&&control.getAttribute('aria-autocomplete'))lookup={target,input:control};
  },true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
