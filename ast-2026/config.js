// Crew sync settings (Firebase Realtime Database).
// Leave as null and the app runs "solo": everything is saved on each phone and
// routes/meetups are shared as text. To turn on live crew sync, follow
// "_About AST 2026.md" in this folder and paste your Firebase web config below.
window.AST_FIREBASE = null;
/* Example — replace with the values from Firebase console › Project settings › Your apps › Web app:
window.AST_FIREBASE = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  databaseURL: "https://your-project-default-rtdb.firebaseio.com",
  projectId: "your-project",
  appId: "1:1234567890:web:abc123"
};
*/
