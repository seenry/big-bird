# Big Bird

Big Bird is a (hopefully useful) package designed to facilitate the quick and convenient creation of basic genetic algorithms in python.

## Examples

### Snake Implementation
Results: https://drive.google.com/drive/folders/1REeKbD_3pZPEwbh0tRJNHyjC2MCwpfBG?usp=sharing

### General Template
```python
import bigbird

# Config Parameters for Big Bird
pop_size = 2000             # Size of each generation's population
layer_counts = [8, 5, 5, 3] # No. of nodes in each layer
m_r8 = 0.3                  # Chance of weight mutation
step_ratio = 1/3.6          # Size of weight perturbation
reinit_r = 0.015            # Chance of weight reinitialization on mutation
immune = 20                 # No. of non-mutated from top of previous generation

# When to automatically stop training
max_generation = 300

# Create a population with configuration parameters
population = bigbird.SimplePopulation(pop_size, layer_counts)

for generation in range(max_generation):
    for bird in population.birds:
        # Evaluates a bird's fitness based on a given input
        bird_inp = your_input_generation_fn()
        bird_out = bird.eval(bird_inp)
        decision = output.tolist().index(max(output))
        bird.fitness = your_fitness_fn(decision)

    # Saves the best performing bird's weight matrices
    champ = sorted(population.birds, key=lambda x: x.fitness)[-1]
    champ.save(fname='./hall-of-fame/champ-' + str(generation) + '.json')

    # Iniitializes next generation
    population.store(immune)
    population.breed()
    population.mutate(m_r8, step_ratio, reinit=reinit_r)
    population.retrieve()
```

Find more examples [here](https://github.com/s2011r2593/big-bird/tree/main/examples)

## License
[MIT](https://choosealicense.com/licenses/mit/)
