import re

with open('kpi_demo.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update total weight logic
html = html.replace('function totW(tasks){return (tasks||getTasks()).reduce((s,t)=>s+t.w,0);}', 
                    'function totW(tasks){return (tasks||getTasks()).filter(t=>!t.isExtra).reduce((s,t)=>s+t.w,0);}')

# 2. Update total score logic
old_totsc = '''function totSc(tasks){
  var t=(tasks||getTasks()).filter(x=>x.sc!==null);
  if(!t.length)return null;
  return Math.round(t.reduce((s,x)=>s+(x.sc*x.w/100),0));
}'''
new_totsc = '''function totSc(tasks){
  var t=(tasks||getTasks()).filter(x=>x.sc!==null);
  if(!t.length)return null;
  var main = t.filter(x=>!x.isExtra).reduce((s,x)=>s+(x.sc*x.w/100),0);
  var extra = t.filter(x=>x.isExtra).reduce((s,x)=>s+(x.sc*x.w/100),0);
  return Math.round(main + extra);
}'''
html = html.replace(old_totsc, new_totsc)

# 3. Add checkbox to Add Modal
old_add_modal = '''<label class="fl">Tỷ trọng đề xuất (%)</label>'''
new_add_modal = '''<label class="fl" style="margin-bottom:8px"><input type="checkbox" id="i-extra" onchange="calcTot()" style="margin-right:6px;vertical-align:middle">Việc phát sinh (Không tính vào 100%)</label>
          <label class="fl">Tỷ trọng / Điểm thưởng đề xuất</label>'''
html = html.replace(old_add_modal, new_add_modal)

# 4. Update calcTot for extra
old_calctot = '''var ex=totW(),nw=parseInt(document.getElementById('i-wt').value)||0,t=ex+nw;'''
new_calctot = '''var isEx = document.getElementById('i-extra').checked;
  var ex=totW(),nw=parseInt(document.getElementById('i-wt').value)||0;
  var t=isEx?ex:(ex+nw);
  if(isEx){ document.getElementById('wt-disp').textContent = '+'+nw+'đ'; document.getElementById('wt-disp').className='wtval ok'; document.getElementById('wt-msg').textContent='Được cộng thêm tối đa vào tổng điểm'; return; }'''
html = html.replace(old_calctot, new_calctot)

# 5. Update addTask
old_addtask = '''if(totW()+w>100)return alert('Tổng tỷ trọng sẽ vượt 100%! Hãy giảm tỷ trọng việc khác trước.');
  KPI_DATA[CU].tasks.push({
    id:Date.now(),name:n,
    bsc:selectedBSC||autoSuggestBSC(n),
    w:w,
    tp:document.getElementById('i-type').value,
    tgt:document.getElementById('i-tgt').value,
    note:document.getElementById('i-note').value,
    st:'pending',pr:0,sc:null
  });'''
new_addtask = '''var isEx = document.getElementById('i-extra').checked;
  if(!isEx && totW()+w>100)return alert('Tổng tỷ trọng việc chính sẽ vượt 100%! Hãy giảm tỷ trọng việc khác trước.');
  KPI_DATA[CU].tasks.push({
    id:Date.now(),name:n,
    bsc:selectedBSC||autoSuggestBSC(n),
    w:w,
    tp:document.getElementById('i-type').value,
    tgt:document.getElementById('i-tgt').value,
    note:document.getElementById('i-note').value,
    st:'pending',pr:0,sc:null,
    isExtra: isEx
  });'''
html = html.replace(old_addtask, new_addtask)

# 6. Update mykpi rows
old_mykpi_row = '''+'<td><input class="wi" type="number" value="'+t.w+'" min="1" max="100" onchange="updW('+t.id+',this.value)" '+(locked?'disabled':'')+'></td>'
    +'<td>'+chip(t.st)+'</td>' '''
new_mykpi_row = '''+'<td><input class="wi" type="number" value="'+t.w+'" min="1" max="100" onchange="updW('+t.id+',this.value)" '+(locked?'disabled':'')+'> '+(t.isExtra?'<span style="font-size:11px;color:var(--w);font-weight:600">điểm thưởng</span>':'%')+'</td>'
    +'<td>'+chip(t.st)+'</td>' '''
html = html.replace(old_mykpi_row, new_mykpi_row)

# 7. Update generic taskTable rows
old_tt_row = '''+'<td><span class="wt">'+t.w+'%</span></td>' '''
new_tt_row = '''+'<td>'+(t.isExtra?'<span class="wt" style="color:var(--w)">+'+t.w+'đ thưởng</span>':'<span class="wt">'+t.w+'%</span>')+'</td>' '''
html = html.replace(old_tt_row, new_tt_row)

# 8. Update detail view
old_dt_row = '''+'<td><input class="wi" type="number" value="'+t.w+'" min="1" max="100" onchange="updWUser(\\''+uk+'\\','+t.id+',this.value)" '+(ps==='approved'?'disabled':'')+'></td>' '''
new_dt_row = '''+'<td><input class="wi" type="number" value="'+t.w+'" min="1" max="100" onchange="updWUser(\\''+uk+'\\','+t.id+',this.value)" '+(ps==='approved'?'disabled':'')+'> '+(t.isExtra?'<span style="color:var(--w);font-size:11px">thưởng</span>':'')+'</td>' '''
html = html.replace(old_dt_row, new_dt_row)

# 9. Clear fields when opening Add
html = html.replace("document.getElementById('i-note').value='';", "document.getElementById('i-note').value='';\n  document.getElementById('i-extra').checked=false;")

with open('kpi_demo.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated successfully")
