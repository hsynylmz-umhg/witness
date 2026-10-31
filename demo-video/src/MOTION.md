Five verbs, exported by motion.ts and nothing else: reveal (a mask edge uncovers content already in place), drawOn (a stroke grows along its length), typeOn (words appear character by character within 15 frames), step (a state changes once; a stated number lands whole in one frame), rule (a hairline is drawn, or carried to a new extent).
Nothing enters from outside the frame, nothing scales, nothing counts up, and the camera never moves; content does not translate while it is revealed.
Two easings only, entrance and state, both in theme.ts; nothing except a draw-on runs longer than 20 frames, and a spring never oscillates.
Matched transitions: 1 to 2, the rule under the opening question becomes the event log's header; 3 to 4, the hash chain's line becomes the baseline of the four figures; 5 to 6, the outline around the cause opens as a mask into the comparison's frame.
The other four boundaries are in-frame reveals: the outgoing beat is covered by a moving edge while the incoming one is drawn in place; no beat cuts on a fade.
Banned: fades or cross-dissolves between beats, slide-ins, fly-ins, zooms, push-ins, spins, bounces, counters, decorative gradients, shadows on type, glowing outlines, particles, node backdrops, lens flares, blue-on-blue glow.
Every colour, size, radius, easing and duration comes from theme.ts; no literal colour or pixel unit appears anywhere else under src.
To add a beat: author it in beats.ts (the slots must still fill 5400 frames), compose it from the five verbs, open it with a reveal or a matched element, and run npm run script-doc.
