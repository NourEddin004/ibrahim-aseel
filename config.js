/* ═══════════════════════════════════════════════════════════════════
   The only file with your Supabase details in it.

   Both pages read this one: the invitation writes replies here, and
   guests.html reads them back. Fill it in once.

   After you edit this file, bump the ?v= number on the two <script>
   tags that load it — one in index.html, one in guests.html — or a
   browser that has already been to the page will keep the old, empty
   copy and the form will silently go nowhere.

     url  — Supabase → Project Settings → Data API → Project URL
     key  — the same page → Project API keys → anon / public

   The anon key is meant to be public. It ships inside this page and
   anyone can read it, which is fine — what it is allowed to DO is set
   by the row-level-security policies in sql/setup.sql, and those let it
   insert a reply and nothing else. It cannot read the guest list, edit
   a row or delete one.

   The key that must never come near this file is the `service_role`
   one on that same settings page. That key ignores every policy.
   ═══════════════════════════════════════════════════════════════════ */
window.INVITE_DB = {
  url  : '',
  key  : '',
  table: 'rsvp',
};
