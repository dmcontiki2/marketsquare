# How check, 2026-10-01 (live site)

*Written by `stories/how_check.py` (HOW-CHECK-1) on the live site BEFORE the HOW-NEAREST-1 / HOW-PLACE-1 / HOW-GATE-F4 ship -- the record of what it found. 100 FAIL, 2 WARN: 91 on Quick's screens; the other 9 are 'the live guide is not the repo's' only because this checkout already carried the fix's guide data.*

## Each guide's own promise

| | Guide | Check |
|---|---|---|
| ok | adventures_guest_house | 19 screens load |
| ok | adventures_guided_walk | 19 screens load |
| ok | cars_bakkie | step 17: Car Purchase Dossier, 3T = live |
| FAIL | cars_bakkie | the live guide is not the repo's (200) |
| ok | cars_bakkie | 22 screens load |
| ok | cars_for_hire | 19 screens load |
| ok | collectors_coins | step 10: Collectables Advert + Market Report, 5T = live |
| FAIL | collectors_coins | the live guide is not the repo's (200) |
| ok | collectors_coins | 22 screens load |
| ok | electrician | gate banner: step 11, 'Tap [[Upload my licence]]' |
| FAIL | electrician | the live guide is not the repo's (200) |
| ok | electrician | 17 screens load |
| ok | home_cleaner | gate banner: step 10, 'Someone you worked for taps [[Yes]]' |
| ok | home_cleaner | 17 screens load |
| FAIL | localmarket_food_preserves | the live guide is not the repo's (200) |
| ok | localmarket_food_preserves | 20 screens load |
| ok | nanny | gate banner: step 12, 'Tap [[Upload my police clearance]]' |
| FAIL | nanny | the live guide is not the repo's (200) |
| ok | nanny | 18 screens load |
| FAIL | plumber | the live guide is not the repo's (200) |
| ok | plumber | 20 screens load |
| FAIL | property_flat | the live guide is not the repo's (200) |
| ok | property_flat | 23 screens load |
| ok | property_house | step 19: Property Area Dossier, 3T = live |
| FAIL | property_house | the live guide is not the repo's (200) |
| ok | property_house | 25 screens load |
| FAIL | tutors_maths | the live guide is not the repo's (200) |
| ok | tutors_maths | 23 screens load |

## Quick's How, screen by screen

### cars_bakkie

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you selling?' | the list |
| ok | make 'Which make?' | cars_bakkie step 3 |
| ok | year 'Roughly what year?' | cars_bakkie step 4 |
| ok | price 'What are you asking?' | cars_bakkie step 5 |
| ok | where 'Which city?' | cars_bakkie step 6 |
| ok | where 'Where is it?' | cars_bakkie step 6 |
| ok | draft 'Here is your listing' | cars_bakkie step 7 |

### cars_bakkie (serves another cars)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you selling?' | the list |
| FAIL | make 'Which make?' | opened the list, not cars_bakkie |
| FAIL | year 'Roughly what year?' | opened the list, not cars_bakkie |
| FAIL | price 'What are you asking?' | opened the list, not cars_bakkie |
| FAIL | where 'Which city?' | opened the list, not cars_bakkie |
| FAIL | where 'Where is it?' | opened the list, not cars_bakkie |
| FAIL | draft 'Here is your listing' | opened the list, not cars_bakkie |

### collectors_coins

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you selling?' | the list |
| ok | cond 'What condition?' | collectors_coins step 3 |
| ok | auth 'Authenticated?' | collectors_coins step 4 |
| ok | price 'What are you asking?' | collectors_coins step 5 |
| ok | where 'Which city?' | collectors_coins step 6 |
| ok | where 'Where are you?' | collectors_coins step 6 |
| ok | draft 'Here is your listing' | collectors_coins step 7 |

### collectors_coins (serves another collectors)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you selling?' | the list |
| FAIL | cond 'What condition?' | opened the list, not collectors_coins |
| FAIL | auth 'Authenticated?' | opened the list, not collectors_coins |
| FAIL | price 'What are you asking?' | opened the list, not collectors_coins |
| FAIL | where 'Which city?' | opened the list, not collectors_coins |
| FAIL | where 'Where are you?' | opened the list, not collectors_coins |
| FAIL | draft 'Here is your listing' | opened the list, not collectors_coins |

### electrician

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| ok | qual 'Which qualification do you have?' | electrician step 3 |
| ok | where 'Which city?' | electrician step 4 |
| ok | where 'Where do you work?' | electrician step 4 |
| ok | how 'What do you charge?' | electrician step 5 |
| ok | draft 'Here is your listing' | electrician step 6 |

### electrician (serves gas_installer)

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| FAIL | qual 'Which qualification do you have?' | opened the list, not electrician |
| FAIL | where 'Which city?' | opened the list, not electrician |
| FAIL | where 'Where do you work?' | opened the list, not electrician |
| FAIL | how 'What do you charge?' | opened the list, not electrician |
| FAIL | draft 'Here is your listing' | opened the list, not electrician |

### home_cleaner

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| ok | where 'Which city?' | home_cleaner step 3 |
| ok | where 'Where can you work?' | home_cleaner step 3 |
| ok | days 'Which days can you work?' | home_cleaner step 4 |
| ok | price 'What do you charge?' | home_cleaner step 5 |
| ok | draft 'Here is your listing' | home_cleaner step 6 |

### localmarket_food_preserves

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you selling?' | the list |
| ok | where 'Which city?' | localmarket_food_preserves step 3 |
| ok | where 'Where are you?' | localmarket_food_preserves step 3 |
| ok | price 'How much?' | localmarket_food_preserves step 4 |
| ok | ship 'How do they get it?' | localmarket_food_preserves step 5 |
| ok | draft 'Here is your listing' | localmarket_food_preserves step 6 |

### localmarket_food_preserves (serves another localmarket)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you selling?' | the list |
| FAIL | where 'Which city?' | opened the list, not localmarket_food_preserves |
| FAIL | where 'Where are you?' | opened the list, not localmarket_food_preserves |
| FAIL | price 'How much?' | opened the list, not localmarket_food_preserves |
| FAIL | ship 'How do they get it?' | opened the list, not localmarket_food_preserves |
| FAIL | draft 'Here is your listing' | opened the list, not localmarket_food_preserves |

### nanny

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| ok | where 'Which city?' | nanny step 3 |
| ok | where 'Where can you work?' | nanny step 3 |
| ok | days 'Which days can you work?' | nanny step 4 |
| ok | price 'What do you charge?' | nanny step 5 |
| ok | draft 'Here is your listing' | nanny step 6 |

### nanny (serves caregiver)

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| FAIL | where 'Which city?' | opened the list, not nanny |
| FAIL | where 'Where can you work?' | opened the list, not nanny |
| FAIL | days 'Which days can you work?' | opened the list, not nanny |
| FAIL | price 'What do you charge?' | opened the list, not nanny |
| FAIL | draft 'Here is your listing' | opened the list, not nanny |

### plumber

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| ok | qual 'Which qualification do you have?' | plumber step 3 |
| ok | where 'Which city?' | plumber step 4 |
| ok | where 'Where do you work?' | plumber step 4 |
| ok | how 'What do you charge?' | plumber step 5 |
| ok | draft 'Here is your listing' | plumber step 6 |

### plumber (serves bricklayer)

| | Screen | How opened |
|---|---|---|
| ok | group 'What kind of work?' | the list |
| ok | what 'Which one are you?' | the list |
| FAIL | qual 'Which qualification do you have?' | opened the list, not plumber |
| FAIL | where 'Which city?' | opened the list, not plumber |
| FAIL | where 'Where do you work?' | opened the list, not plumber |
| FAIL | how 'What do you charge?' | opened the list, not plumber |
| FAIL | draft 'Here is your listing' | opened the list, not plumber |

### property_flat

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you listing?' | the list |
| ok | deal 'To sell, or to let?' | property_flat (sale or let is not chosen yet) |
| ok | beds 'How many bedrooms?' | property_flat step 4 |
| WARN | baths 'How many bathrooms?' | property_flat step 4 -- no card of its own; the last card she passed |
| ok | where 'Which city?' | property_flat step 5 |
| ok | where 'Where is it?' | property_flat step 5 |
| ok | price 'What is the rent a month?' | property_flat step 6 |
| ok | draft 'Here is your listing' | property_flat step 7 |

### property_flat (a house to let)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you listing?' | the list |
| ok | deal 'To sell, or to let?' | property_house (sale or let is not chosen yet) |
| FAIL | beds 'How many bedrooms?' | opened property_house, not property_flat |
| FAIL | baths 'How many bathrooms?' | opened property_house, not property_flat |
| FAIL | where 'Which city?' | opened property_house, not property_flat |
| FAIL | where 'Where is it?' | opened property_house, not property_flat |
| FAIL | price 'What is the rent a month?' | opened property_house, not property_flat |
| FAIL | draft 'Here is your listing' | opened property_house, not property_flat |

### property_flat (serves another property)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you listing?' | the list |
| FAIL | deal 'To sell, or to let?' | opened the list, not property_flat |
| FAIL | beds 'How many bedrooms?' | opened the list, not property_flat |
| FAIL | baths 'How many bathrooms?' | opened the list, not property_flat |
| FAIL | where 'Which city?' | opened the list, not property_flat |
| FAIL | where 'Where is it?' | opened the list, not property_flat |
| FAIL | price 'What is the rent a month?' | opened the list, not property_flat |
| FAIL | draft 'Here is your listing' | opened the list, not property_flat |

### property_house

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you listing?' | the list |
| ok | deal 'To sell, or to let?' | property_house (sale or let is not chosen yet) |
| ok | beds 'How many bedrooms?' | property_house step 4 |
| WARN | baths 'How many bathrooms?' | property_house step 4 -- no card of its own; the last card she passed |
| ok | where 'Which city?' | property_house step 5 |
| ok | where 'Where is it?' | property_house step 5 |
| ok | price 'What is your asking price?' | property_house step 6 |
| ok | draft 'Here is your listing' | property_house step 7 |

### property_house (a flat to sell)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you listing?' | the list |
| ok | deal 'To sell, or to let?' | property_flat (sale or let is not chosen yet) |
| FAIL | beds 'How many bedrooms?' | opened property_flat, not property_house |
| FAIL | baths 'How many bathrooms?' | opened property_flat, not property_house |
| FAIL | where 'Which city?' | opened property_flat, not property_house |
| FAIL | where 'Where is it?' | opened property_flat, not property_house |
| FAIL | price 'What is your asking price?' | opened property_flat, not property_house |
| FAIL | draft 'Here is your listing' | opened property_flat, not property_house |

### property_house (serves another property)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you listing?' | the list |
| FAIL | deal 'To sell, or to let?' | opened the list, not property_house |
| FAIL | beds 'How many bedrooms?' | opened the list, not property_house |
| FAIL | baths 'How many bathrooms?' | opened the list, not property_house |
| FAIL | where 'Which city?' | opened the list, not property_house |
| FAIL | where 'Where is it?' | opened the list, not property_house |
| FAIL | price 'What is your asking price?' | opened the list, not property_house |
| FAIL | draft 'Here is your listing' | opened the list, not property_house |

### tutors_maths

| | Screen | How opened |
|---|---|---|
| ok | what 'What do you teach?' | the list |
| ok | level 'Which level?' | tutors_maths step 3 |
| ok | mode 'Online or in person?' | tutors_maths step 4 |
| ok | price 'What do you charge?' | tutors_maths step 5 |
| ok | where 'Which city?' | tutors_maths step 6 |
| ok | where 'Where are you?' | tutors_maths step 6 |
| ok | draft 'Here is your listing' | tutors_maths step 7 |

### tutors_maths (serves another tutors)

| | Screen | How opened |
|---|---|---|
| ok | what 'What do you teach?' | the list |
| FAIL | level 'Which level?' | opened the list, not tutors_maths |
| FAIL | mode 'Online or in person?' | opened the list, not tutors_maths |
| FAIL | price 'What do you charge?' | opened the list, not tutors_maths |
| FAIL | where 'Which city?' | opened the list, not tutors_maths |
| FAIL | where 'Where are you?' | opened the list, not tutors_maths |
| FAIL | draft 'Here is your listing' | opened the list, not tutors_maths |

### Find in cars

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you after?' | the list |
| FAIL | price 'What can you spend?' | cars_bakkie opened step 5, not step 13 |
| FAIL | where 'Which city?' | cars_bakkie opened step 6, not step 13 |
| FAIL | where 'Where do you want to look?' | cars_bakkie opened step 6, not step 13 |
| FAIL | draft 'Only examples so far' | cars_bakkie opened step 7, not step 13 |

### Find in collectors

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you hunting?' | the list |
| FAIL | price 'What can you spend?' | collectors_coins opened step 5, not step 15 |
| FAIL | rare 'How rare?' | collectors_coins opened step 5, not step 15 |
| FAIL | draft 'Which city?' | collectors_coins opened step 7, not step 15 |

### Find in localmarket

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you looking for?' | the list |
| FAIL | where 'Which city?' | localmarket_food_preserves opened step 3, not step 14 |
| FAIL | where 'Which area?' | localmarket_food_preserves opened step 3, not step 14 |
| FAIL | price 'What can you spend?' | localmarket_food_preserves opened step 4, not step 14 |
| FAIL | draft 'Yes — 1 on TrustSquare' | localmarket_food_preserves opened step 6, not step 14 |

### Find in property

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you after?' | the list |
| ok | deal 'Buying or renting?' | property_house (sale or let is not chosen yet) |
| FAIL | where 'Which city?' | property_house opened step 5, not step 14 |
| FAIL | where 'Which area?' | property_house opened step 5, not step 14 |
| FAIL | draft 'Only examples so far' | property_house opened step 7, not step 14 |

### Find in services

| | Screen | How opened |
|---|---|---|
| ok | group 'What do you need?' | the list |
| ok | what 'Who do you need?' | the list |
| FAIL | where 'Which city?' | home_cleaner opened step 3, not step 14 |
| FAIL | where 'Which area?' | home_cleaner opened step 3, not step 14 |
| FAIL | when 'How soon?' | home_cleaner opened step 3, not step 14 |
| FAIL | draft 'Only examples so far' | home_cleaner opened step 6, not step 14 |

### Find in tutors

| | Screen | How opened |
|---|---|---|
| ok | what 'What do they need?' | the list |
| FAIL | level 'Which level?' | tutors_maths opened step 3, not step 15 |
| FAIL | where 'Which city?' | tutors_maths opened step 6, not step 15 |
| FAIL | where 'Where?' | tutors_maths opened step 6, not step 15 |
| FAIL | draft 'Only examples so far' | tutors_maths opened step 7, not step 15 |

### Quick stay (B&B / guest house)

| | Screen | How opened |
|---|---|---|
| ok | what 'What are you offering?' | the list |
| FAIL | kind 'What kind of place?' | opened adventures_guest_house -- a guide walked in TrustSquare's Sell, at step 1 |
| FAIL | price 'Per room, per night?' | opened adventures_guest_house -- a guide walked in TrustSquare's Sell, at step 1 |
| FAIL | where 'Which city?' | opened adventures_guest_house -- a guide walked in TrustSquare's Sell, at step 1 |
| FAIL | where 'Where is it?' | opened adventures_guest_house -- a guide walked in TrustSquare's Sell, at step 1 |
| FAIL | draft 'Here is your listing' | opened adventures_guest_house -- a guide walked in TrustSquare's Sell, at step 1 |

