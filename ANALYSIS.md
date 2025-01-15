# Tweaking the 1.0 automa

1.0 Goals
  - Automa has low upkeep
  - Remove the need to block up sections of the map during setup
  - Maintain the regular rules of the game

1.0 Flaws
  - The automa doesn't block enough city spaces
  - The automa doesn't drain the resource market enough

1.0+ Ideas
  - Remove the original goal of not blocking regions
    - In play testing, you need to put down dozens of automa houses to effectively do the same thing as blocking regions at the start
  - Change the way the automa pulls resources
    - Instead of a flat mult and 1 power plant per simulated player, have the automa expose more plants per rounds and use those

# 1.0+ Design Thoughts

Let's think about the simulated player count. Originally I wanted 4 simulated players.
That would means at 1p and 2p no cards are removed from the plant deck and all regions could be used.

Looking at the numbers, 2p and 3p are not great. 2p has 10/21 for step 2 and end game. 3p has 7 and 17 for end game. I do like that 3p and 4p have the same step 2 and end game triggers. That would be one less thing to balance (the automa's rate of gaining points).

It might make sense to have a 1p and 2p deck, but I like keeping things simple and only needing a single deck.

Maybe the automa has two stacks of plants. It a new purchase is higher, then it goes top the stack. Otherwise it goes bottom the stack.