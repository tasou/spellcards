from collections import namedtuple

Spell = namedtuple(
    'Spell',
    ['level',
     'school',
     'casting_time',
     'components',
     'effect',
     'duration',
     'saving_throw',
     'spell_resistance',
     'range',
     'description']
)