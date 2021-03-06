from hypnopyze.styles.manager import StyleManager
from hypnopyze.scales.blueprint import *
from hypnopyze.patterns.pattern import *
from hypnopyze.notes import *


# Builder for Pattern objects.
class PatternBuilder:
    def __init__(self):
        #
        # intermediate pattern data
        #

        self.name = ""
        self.bars = 1  # bars in the pattern
        self.i = []  # indices
        self.v = []  # velocity
        self.d = []  # duration
        self.repeat = False  # repeatable
        self.real_time = False

        #
        # index types
        #

        # if use_directions, use directions and generate a couple
        # of variations per pattern
        self.use_directions = True

        # if use_walks and not use_directions, just walk the scale
        self.use_walks = False

        # if not use_directions and not use_walks, pattern is treated
        # as MIDI sounds

        #
        # directions -> walks
        #

        # walks to generate from one set  of directions
        self.num_walks = 20

        #
        # walks -> sounds
        #

        self.key = E
        self.scale = MajorScale
        self.base_octave = DEFAULT_OCTAVE

        # set this to None if the scale changes
        self.walker = None

        #
        # out
        #

        self.patterns = []

        #
        # register
        #

        # instrument name for registering with the style manager
        self.instrument = "lead"

    # Builds the patterns. Returns the number of patterns built.
    def build(self) -> int:

        prng = StyleManager().prng

        if not self.walker:
            self.walker = ScaleWalker(
                Scale(ScaleBlueprint(self.scale), self.key))

        base_pattern = Pattern(self.name,
                               self.bars,
                               self.i,
                               self.v,
                               self.d,
                               self.repeat,
                               self.real_time)

        walks = []
        if self.use_directions:
            walks = [base_pattern.walk_from_these_directions(len(self.scale),
                                                             prng)
                     for _ in range(0, self.num_walks)]

            walks = list(set(walks))
        elif self.use_walks:
            walks = [base_pattern]

        sounds = []

        if self.use_directions or self.use_walks:
            for walk in walks:
                self.walker.jump(self.base_octave)
                sounds.append(
                    walk.sound_pattern_from_this_walk(self.walker))
        else:
            sounds = [base_pattern]

        sounds = [i for i in sounds if i]

        self.patterns.extend(sounds)
        return len(sounds)

    # Registers the built patterns with the StyleManager
    def register(self):
        if not self.patterns:
            print("No patterns to register.")
        else:
            StyleManager().pattern_collection.add_patterns(self.instrument,
                                                           self.patterns)
            self.patterns.clear()

    def build_and_register(self):
        self.build() and self.register()
