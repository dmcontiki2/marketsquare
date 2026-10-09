#!/usr/bin/env python3
"""trainer_photo_prompts.py -- TRAINER-PHOTOS-1 (David, 10 Oct 2026): the trainer roles' pictures become real-looking
photos of the coaching itself -- "chess coach with chess set and clock, judo with judo looking trainer and child in
right gear etc." -- generated on the Higgsfield balance David set aside ("i still have $15 for Higgsfield photos").

This AMENDS RUL-157 for the Trainers door only: a coach's picture shows the coach and the people being coached, because
coaching is people working together; Services pictures keep RUL-157 as ruled (the work, never a person). PHOTO-ANON-1 and
SO-1 still hold: nobody recognisable (faces turned away, from behind, side-on or soft), no text, no logos, no brands;
a child is shown only in the sports commonly coached to children, fully in the sport's proper kit, in a supervised,
everyday training scene.

Imported by scripts/build_role_registry.py, which writes these prompts into roles/role_registry.json (role_picture.prompt);
scripts/gen_role_pictures.py --go then makes them.
"""
STYLE = ("Photorealistic photograph, natural light, an everyday coaching session at a community club that could be anywhere "
         "in the world. Subject: {subject}. The sport must be instantly recognisable from the kit, the equipment and the "
         "place. NO recognisable faces: people are seen from behind, side-on, at a distance or with faces turned away or "
         "softly out of focus. Anyone under 18 is fully dressed in the sport's proper kit, in a safe, supervised, ordinary "
         "training moment. No text, no letters, no numbers on shirts, no logos, no brand names, no watermarks. Square 1:1, "
         "clean composition, warm, encouraging and dignified mood.")

SUBJECT = {
 "personal_trainer": "a personal trainer spotting an adult client doing dumbbell presses on a bench in a bright gym",
 "aerobics_instructor": "an aerobics instructor leading a small group of adults on step platforms in a sunny studio, seen from behind the class",
 "dance_fitness_instructor": "a dance fitness instructor mid-move in front of a group of adults dancing in a studio with a sprung wooden floor",
 "yoga_instructor": "a yoga instructor gently adjusting an adult's pose on a mat in a calm studio with plants",
 "pilates_instructor": "a Pilates instructor guiding an adult client on a reformer machine in a light studio",
 "functional_fitness_coach": "a coach watching adults swing kettlebells and use battle ropes in a functional training gym",
 "strength_conditioning_coach": "a strength coach beside an athlete lifting a barbell off a platform, chalk in the air",
 "boxing_coach": "a boxing coach holding pads for an adult boxer in red gloves in a gym ring",
 "kickboxing_coach": "a kickboxing coach holding a kick shield while an adult in shin guards and gloves kicks it",
 "wrestling_coach": "a wrestling coach kneeling on a mat showing two teenagers in singlets and headgear a starting stance",
 "judo_instructor": "a judo instructor in a white judogi and black belt teaching a child in a white judogi and belt a throw on a tatami",
 "karate_instructor": "a karate instructor in a white gi and black belt guiding a row of children in white gis through a kata in a dojo",
 "taekwondo_instructor": "a taekwondo instructor holding a kicking paddle for a child in a dobok and head guard on a blue mat",
 "jiu_jitsu_instructor": "a jiu-jitsu instructor in a gi demonstrating a hold to an adult student on a grappling mat",
 "mma_coach": "an MMA coach holding pads for an adult fighter in fingerless gloves inside a training cage",
 "fencing_coach": "a fencing coach in white fencing gear and mask giving a lesson to a young fencer in full white kit and mask on a piste",
 "soccer_coach": "a soccer coach with a whistle setting out cones for a group of children in football kit on a green pitch",
 "rugby_coach": "a rugby coach passing a ball to a group of teenagers in rugby jerseys on a grass field with posts behind",
 "cricket_coach": "a cricket coach in the nets feeding balls to a young batter in pads and helmet",
 "hockey_coach": "a field hockey coach showing a group of children with sticks and shin guards how to dribble on a turf pitch",
 "netball_coach": "a netball coach with girls in bibs practising shooting at a netball hoop on an outdoor court",
 "basketball_coach": "a basketball coach with a group of children dribbling basketballs on a polished indoor court",
 "volleyball_coach": "a volleyball coach tossing a ball to teenagers practising a dig in a sports hall",
 "baseball_coach": "a baseball coach pitching soft throws to a young batter in a helmet on a diamond",
 "american_football_coach": "an American football coach with teenagers in helmets and pads running a drill on a turf field",
 "tennis_coach": "a tennis coach feeding balls from a basket to a child with a racket on a hard court",
 "squash_coach": "a squash coach and a teenage player in eye protection rallying on a wooden squash court, seen from behind the glass",
 "padel_coach": "a padel coach giving a lesson to two adults with padel rackets on a glass-walled padel court",
 "badminton_coach": "a badminton coach hitting a shuttlecock to a child with a racket on an indoor court",
 "table_tennis_coach": "a table tennis coach rallying with a child at a blue table in a club hall",
 "golf_coach": "a golf coach helping a teenager with their grip and swing on a driving range at sunrise",
 "archery_coach": "an archery coach standing beside an adult archer drawing a recurve bow towards a target on a range",
 "swimming_coach": "a swimming coach on the pool deck guiding children in caps and goggles swimming in lanes of an outdoor pool",
 "diving_instructor": "a scuba instructor and an adult diver in full scuba gear giving the OK signal in clear blue water",
 "surfing_coach": "a surf coach in the shallows steadying a surfboard for a child in a wetsuit catching a small wave",
 "rowing_canoeing_coach": "a coach on a jetty watching adults paddle canoes on a calm dam at dawn",
 "sailing_instructor": "a sailing instructor in a small boat beside a teenager sailing a small dinghy on a lake",
 "running_athletics_coach": "an athletics coach with a stopwatch watching children in running kit sprint on a track",
 "cycling_coach": "a cycling coach riding alongside a group of adult road cyclists in helmets on a quiet road at sunrise",
 "triathlon_coach": "a triathlon coach at a transition rack with an adult athlete changing from bike to running shoes",
 "horse_riding_instructor": "a riding instructor holding the lead rein of a pony ridden by a child in a riding helmet in an arena",
 "climbing_instructor": "a climbing instructor belaying a child in a harness and helmet climbing an indoor climbing wall",
 "skating_coach": "a skating coach holding the hands of a child in skates and a helmet on an ice rink",
 "ski_snowboard_instructor": "a ski instructor leading a line of children in helmets and goggles down a gentle snowy slope",
 "gymnastics_coach": "a gymnastics coach watching a child in a t-shirt and gym shorts do a cartwheel on a floor mat, a balance beam and bars behind them in a gym hall",   # leotard wording refused by the image service, 10 Oct
 "acrobatics_coach": "an acrobatics coach spotting a child doing a handstand on a tumbling track with crash mats",
 "chess_coach": "a chess coach pointing at a wooden chess board with a chess clock beside it while a child studies the position",
}
