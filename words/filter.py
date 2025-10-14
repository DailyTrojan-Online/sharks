filename = "2of12.txt"
bad = "bad.txt"
list = []
questionable = []
swears = [
    "anal",
    "anus",
    "arse",
]
with open(bad, "r") as file:
    for line in file:
        swears.append(line.strip())


with open(filename, "r") as file:
    for line in file:
        word = line.strip()
        if len(word) >= 4 and "-" not in word:  # Filter words with 4 or more letters
            if(word in swears):
                questionable.append(word)
            else:
                list.append(word)

# Save the filtered words to a new file
with open("filtered_words.js", "w") as file:
    file.write("export const words = [\n")
    for word in list:
        file.write(f'    "{word}",\n')
    file.write("];\n")

with open("questionable_words.js", "w") as file:
    file.write("export const questionable = [\n")
    for word in questionable:
        file.write(f'    "{word}",\n')
    file.write("];\n")