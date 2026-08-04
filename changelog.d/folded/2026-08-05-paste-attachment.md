## 2026-08-05 — Paste a screenshot into a fault report (MAINT-B1b addendum)

**David:** *"instead of having a complex (not complaining) can't we just have a paste option?
open report, say 'the view button doesn't work', snip the button and paste it?"*

He was right twice in one evening. The `getDisplayMedia` capture button is gone — it achieved the
same end but demanded a permission prompt and a window choice before it would do anything, to
replace `Win+Shift+S` then `Ctrl+V`, which Windows users already know. Now the sheet accepts a
clipboard image pasted anywhere inside it. Drag-and-drop rides the same handler for free; the file
picker survives as a quiet link for phones, where pasting is not the natural gesture.

**Then he found the real defect:** *"it pasted something but I could not identify it as the snippy."*
Read from his live browser, the paste HAD worked — thumbnail present, drop zone reading *Screenshot
attached*. It rendered **below the fold of the scrolling sheet**, so from where he was looking
nothing happened. **An attachment that confirms itself out of sight is the same as no attachment.**
The preview is now a green-framed card headed *"This is what you are attaching"*, matted on dark
navy so a pale snip still reads, with a Remove button — and `attach()` scrolls it into view and
writes a confirmation next to the send button, where the eye already is.

**Verified end-to-end in a real Chromium (Playwright), not by inspection:** the tab renders on the
flag, the sheet opens, a synthesised clipboard paste attaches, the preview is shown *and*
`inViewport` is true, and Remove detaches cleanly. Three rounds on one feature, each a real defect
the previous check could not see — which is the argument for driving the browser rather than
reasoning about it.

**The form is now three things:** what's wrong, your email, `Ctrl+V`.
