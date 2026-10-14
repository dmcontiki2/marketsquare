## 2026-10-13 — A code sign-in shows her own Tuppence at once (SIGNIN-BALANCE-1)

David, 13 Oct 2026, after signing in with a code: *"Why have i again lost my Tuppence account?"* and *"Does this happen to
all users? They cant like me fix it instantly"*. His 359T were untouched; the screen showed the old figure. Three of the
four code sign-in boxes (Quick's proof step, the go-live proof, the sell flow's sign-in) wrote the new email and carried
on without reading the balance, so anyone signing in there saw 0T (or the previous account's figure after a switch) until
a reload. All four now go through `msSignedInAs()`: a different person clears the previous one's saved details first,
then her balance is read from the server straight away. Regression ledger RG-0972.
