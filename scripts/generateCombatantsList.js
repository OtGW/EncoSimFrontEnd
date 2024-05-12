const fs = require("fs")
const path = require("path")
const directoryPath = path.join(__dirname, "../public/Entities")
const outputFile = path.join(__dirname, "../public/combatantsFilenames.json")

fs.readdir(directoryPath, (err, files) => {
  if (err) throw err
  fs.writeFile(outputFile, JSON.stringify(files), (err) => {
    if (err) throw err
    console.log(
      "Filenames from Entities project folder have been saved as list to combatantsFilenames.json file in public directory!"
    )
  })
})
