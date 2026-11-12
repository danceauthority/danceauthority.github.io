/**
 * @OnlyCurrentDoc
 */
// Shared storage for the Big Bend + Santa Fe trip page.
// Paste into the trip Google Sheet: Extensions > Apps Script, replace everything, save,
// then Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone.
// The trip code lives in the sheet's Settings tab (cell B1), not here.
// @OnlyCurrentDoc above limits this script to this one spreadsheet: it cannot see
// any of your other Sheets or anything else in your Drive.
// The full plan is kept as JSON in Data!A1; the Plans, Hard dates and Ideas tabs are
// readable copies rewritten on every save.

function doGet() {
  return json_(load_());
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var req = JSON.parse(e.postData.contents);
    var code = String(sheet_('Settings').getRange('B1').getValue()).trim();
    if (!code || String(req.code || '').trim() !== code) return json_({error: 'bad code'});
    if (req.op && req.op.type === 'inbox') {
      inbox_(req.op);
      return json_(load_());
    }
    var doc = load_();
    applyOp_(doc, req.op);
    doc.updated = new Date().toISOString();
    sheet_('Data').getRange('A1').setValue(JSON.stringify(doc));
    mirror_(doc);
    return json_(doc);
  } catch (err) {
    return json_({error: String(err)});
  } finally {
    lock.releaseLock();
  }
}

function load_() {
  var raw = sheet_('Data').getRange('A1').getValue();
  return raw ? JSON.parse(raw) : {};
}

function applyOp_(doc, op) {
  if (op.type === 'init') { if (!doc.families) { doc.families = op.doc.families; doc.hardDates = op.doc.hardDates; doc.ideas = op.doc.ideas; doc.reservations = op.doc.reservations || []; } return doc; }
  if (!doc.families) doc.families = {};
  if (!doc.hardDates) doc.hardDates = [];
  if (!doc.ideas) doc.ideas = [];
  if (op.type === 'setPlan') { doc.families[op.family] = doc.families[op.family] || {}; doc.families[op.family].plan = op.plan; }
  if (!doc.reservations) doc.reservations = [];
  if (op.type === 'addRes') doc.reservations.push(op.item);
  if (op.type === 'removeRes') doc.reservations = doc.reservations.filter(function (r) { return r.id !== op.id; });
  if (op.type === 'addHard') doc.hardDates.push(op.item);
  if (op.type === 'removeHard') doc.hardDates = doc.hardDates.filter(function (h) { return h.id !== op.id; });
  if (op.type === 'addIdea') doc.ideas.push(op.item);
  if (op.type === 'removeIdea') doc.ideas = doc.ideas.filter(function (i) { return i.id !== op.id; });
  if (op.type === 'updateIdea') doc.ideas.forEach(function (i) { if (i.id === op.id) ['status', 'title', 'note', 'date', 'place', 'lat', 'lng'].forEach(function (k) { if (k in op.fields) i[k] = op.fields[k]; }); });
  if (op.type === 'vote') doc.ideas.forEach(function (i) { if (i.id === op.id) { i.votes = i.votes || {}; if (op.on) i.votes[op.family] = true; else delete i.votes[op.family]; } });
  return doc;
}

function mirror_(doc) {
  var plans = [['Family', 'Place', 'Arrive', 'Leave', 'Note']];
  Object.keys(doc.families || {}).forEach(function (f) {
    ((doc.families[f] || {}).plan || []).forEach(function (s) { plans.push([f, s.place, s.start, s.end, s.note]); });
  });
  write_('Plans', plans);
  var hard = [['Date', 'What', 'Added by']];
  (doc.hardDates || []).forEach(function (h) { hard.push([h.date, h.label, h.by]); });
  write_('Hard dates', hard);
  var ideas = [['Idea', 'Details', 'Date', 'Place', 'Posted by', 'Status', '+1s']];
  (doc.ideas || []).forEach(function (i) { ideas.push([i.title, i.note, i.date, i.place, i.by, i.status, Object.keys(i.votes || {}).join(', ')]); });
  write_('Ideas', ideas);
  var res = [['Family', 'Type', 'Place', 'Check in', 'Check out', 'Site / room', 'Confirmation #', 'Note']];
  (doc.reservations || []).forEach(function (r) { res.push([r.family, r.kind, r.place, r.start, r.end, r.detail, r.conf, r.note]); });
  write_('Reservations', res);
}

// Pasted confirmations and links. Kept private: written only to the
// 'Reservation inbox' tab, never into the public plan data.
function inbox_(op) {
  var sh = sheet_('Reservation inbox');
  if (sh.getLastRow() === 0) sh.appendRow(['Received', 'Family', 'Pasted text or link', 'Merged?']);
  sh.appendRow([new Date(), op.family, op.text || '', '']);
}

function write_(name, rows) {
  var sh = sheet_(name);
  sh.clearContents();
  sh.getRange(1, 1, rows.length, rows[0].length).setNumberFormat('@').setValues(rows);
}

function sheet_(name) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
