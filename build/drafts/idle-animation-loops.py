"""UNPUBLISHED DRAFT — awaiting the founder's approval.
Blog posts are editorial and are never published without an explicit yes.
This folder is in _config.yml's exclude list, so nothing here is served.
To publish: paste this dict at the top of POSTS in build/blog.py, run
python3 build/blog.py, add both URLs to sitemap.xml, then commit and push.
Verified 2026-11-06: builds clean, Lighthouse 99/100/100/100, CLS 0,
1,346 words, 7 h2s none of which collide with the five live posts.
"""

DRAFT = dict(
 slug='idle-animation-loops',
 date='2026-11-06',
 updated='2026-11-06',
 title='One animation loop costs the same as ten',
 h1='One animation loop costs the same as ten',
 sub='Left on a desk, our game kept redrawing sixty times a second. We switched off one of the eight animations running on that screen and measured again. Nothing moved.',
 desc='Our idle game screen drew 60 frames a second. Switching off one of its eight animation loops saved nothing — the cost is per screen, not per animation.',
 body="""
      <p>Leave Wordmere open on a table and walk away. Nothing moves that you would really notice. A letter chip swells slightly and settles. A disc breathes. A flame flickers on the streak counter. The screen looks still.</p>

      <p>It was drawing sixty frames a second, indefinitely, and spending about a third of a CPU core to do it.</p>

      <p>That is the sort of thing that surfaces as a one-star review about battery on a four-year-old Android phone and surfaces nowhere else. So in October we sat down to measure it properly, expecting to come away with a ranked list of expensive animations to go and fix. We got something more useful and a lot less convenient.</p>

      <h2>Eight loops, and switching one off changed nothing</h2>

      <p>First we counted the infinite loops on the two screens people actually sit on. A level has the letter-chip breath, the disc breathe, an idle nudge that starts after six seconds and then runs forever, and a rescue cell that spins and pops once you have stalled. Three more appear only in certain states: a halo on the plane, the ads-free slot, the piggy pill. The home screen has two, the streak flame and the daily tile's flip and glow.</p>

      <p>Then we switched them off one at a time and measured every configuration.</p>

      <p>Switching off a single loop while any other was still running saved approximately nothing. Not a small amount — an amount we could not separate from the noise in the measurement. Switch all of them off and the screen dropped to zero frames per second and two to five per cent of a core. Switch any one of them back on, it genuinely did not matter which, and we were back to drawing on every vsync at twenty-five to thirty-five per cent.</p>

      <p>I had assumed the cost would be roughly proportional to the number of animations running. It is not proportional at all. It is a step, and the step is at one.</p>

      <h2>Why the saving is not additive</h2>

      <p>This is obvious once you have seen it, which is the most irritating kind of obvious.</p>

      <p>A frame is a whole-screen unit of work. Once anything has invalidated the view for this vsync, the pipeline does its pass — layout, draw, upload, composite — more or less regardless of how much of the screen actually changed. The second animation is joining a frame that was going to be drawn anyway, so it is close to free. The first one is not, because the first one is what turns the frame on.</p>

      <p>So "how expensive is this animation" is the wrong question to profile. The expensive thing is not any particular animation. It is the existence of any animation at all, and one loop makes that decision on behalf of the entire screen.</p>

      <p>Which is why per-component optimisation cannot help you here. You can make every animation on the screen twice as efficient and save nothing worth measuring, because you have not changed the number of frames.</p>

      <div class="pull"><p>The cost is not in the animation. It is in the decision to draw a frame at all — and a single loop makes that decision for everything else on the screen.</p></div>

      <h2>The measurement I had to throw away</h2>

      <p>A study we had run a few weeks earlier, looking at a video backdrop, reported the home screen holding 72 to 76 frames a second. Two things are wrong with that sentence and I wrote it.</p>

      <p>The capture windows labelled "Home" were not the home screen. They were level 2. Wrong screen, confidently labelled.</p>

      <p>The other problem is worse, because it was visible on the page. A 60 Hz display cannot show you 76 frames a second. That number should have stopped me cold, and instead it sat in a table for a month looking like data. It was an artefact of how we were counting frames; the real figure was about sixty.</p>

      <p>What caught it in the end was the new study producing clean zeros. Zero is a hard number to arrive at by accident, and once we had one we could see that the earlier table had never been measuring what it claimed.</p>

      <h2>Kill switches beat rebuilds</h2>

      <p>None of this would have been practical with a normal build loop. Eight loops is a lot of combinations, and if each one costs you a twenty-minute native build you will measure three of them and reason your way to the rest. Reasoning your way to the rest is exactly how we got the 76 fps table.</p>

      <p>So we built two bits of throwaway tooling first. A deep link that toggles individual loops at runtime, roughly <code>wordmere://qa-idle?off=wheel,flame</code>, and a script that injects a fresh JavaScript bundle into an already-built APK. Together those turned a configuration change from a rebuild into about thirty seconds.</p>

      <p>While we were in there we found four animated components still sitting in the tree that nothing imports any more. They cost exactly nothing, because they never render. We had been carrying them for months and would have happily profiled them.</p>

      <h2>Settling, not deleting</h2>

      <p>The blunt fix is to delete animations. That is a product decision wearing a performance costume, and the breathing chips are part of how the game feels to play. We did not want to pay for battery with character.</p>

      <p>What shipped instead is a screen-wide idle rule. Every loop rests fifteen seconds after the last touch. The hint nudge pulses three times rather than forever. The flame burns for four seconds. The daily tile flips once instead of on a cycle. Touch anything and the whole screen wakes up.</p>

      <p>On the emulator a level now sits around fifty frames a second while you are playing, falls to zero fifteen seconds after you stop, and returns to sixty-two the instant you tap. The home screen reaches zero about four seconds in, once the flame has finished. Both platforms behave the same way.</p>

      <p>One detail worth knowing if you use Reanimated: <code>withRepeat</code> already respects the system Reduce Motion setting by default. Every player who had that switch turned on had been getting the idle behaviour free the entire time. We had shipped a battery feature by accident and filed it under accessibility.</p>

      <h2>What this does not fix</h2>

      <p>The figures above are emulator figures, on API 35. The shape of the result holds — all-or-nothing is a property of how frames work, not of that machine — but do not expect the percentages to match a real handset.</p>

      <p>It does nothing at all for anyone actively playing, and that is on purpose. During play the screen should animate. We only fixed the case where the game is open and nobody is touching it, which happens more than you would think: a level left on screen while someone answers the door, the home screen while they decide whether to keep going.</p>

      <p>It also leaves two things alone. The video backdrop is a separate problem that we measured separately. And the music costs three to five per cent of a core on its own, which no amount of frame work touches.</p>

      <p>Finally, an honest deduction from our own result: animations built as a burst followed by a hold were already cheap, because a hold draws no frames. Some of what we "fixed" was not costing much to begin with. The win came from the loops that never stopped, not from the ones that paused.</p>

      <h2>Measure the screen, not the component</h2>

      <p>If you are profiling a UI with several animations running, measure configurations rather than components. The question "which of these is the expensive one" may simply have no answer, and you can lose a week looking for it.</p>

      <p>The question that does have an answer is how many frames the screen draws when nobody is touching it, and what the smallest change is that takes that number to zero.</p>

      <p>Zero, not fewer. Fewer frames is a different and much worse outcome, because it costs you the same wake-ups and gives you a visibly choppier animation. Either the screen is alive or it is asleep.</p>""")
