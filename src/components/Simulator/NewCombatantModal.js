import {
  Modal,
  TextInput,
  NumberInput,
  Checkbox,
  Button,
  Select,
  Group,
  Box,
  Title,
  SimpleGrid,
  Tooltip,
  Divider,
  Card,
} from "@mantine/core"
import { useForm } from "@mantine/form"

function NewCombatantModal({ opened, setOpened }) {
  const form = useForm({
    initialValues: {
      name: "",
      ac: 10,
      hp: 10,
      proficiency: 2,
      level: 1,
      heroOrVillain: 0,
      characterType: "normal",
      attackModifier: 5,
      attackDamage: 7.5,
      attackNumber: 1,
      offHandDamage: 0,
      usesRangeAttacks: false,
      spellMod: 0,
      spellDC: 10,
      spellSlots: Array(9).fill(0), // Array for spell slots levels 1-9
      position: "Front",
      dmgType: "slashing",
      dmgResistances: {
        acid: false,
        cold: false,
        // Add other damage types
      },
      strategyLevel: 2,
      otherAbilities: "",
    },
    validate: {
      name: (value) => (value ? null : "Character name is required"),
      ac: (value) => (value > 0 ? null : "Armor Class must be greater than 0"),
      // Add other validations here
    },
  })

  const handleSubmit = (values) => {
    console.log(values)
    // Handle form submission, e.g., API call or state update
  }

  return (
    <Modal
      opened={opened}
      onClose={() => setOpened(false)}
      title="Create, Modify, or Delete Combatant"
      size="xl"
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          withAsterisk
          required
          label="Combatant Name"
          placeholder="Enter combatant name"
          {...form.getInputProps("name")}
        />
        <SimpleGrid cols={4} spacing="lg">
          <Card shadow="md" padding="md">
            <Title order={3}>Basic Stats</Title>
            <NumberInput label="Armor Class (AC)" {...form.getInputProps("ac")} />
            <NumberInput label="Health Points (HP)" {...form.getInputProps("hp")} />
            <NumberInput label="Proficiency" {...form.getInputProps("proficiency")} />
            <Tooltip
              position="left"
              withArrow
              multiline
              width={220}
              label="The character level or CR of the combatant. Some functions and abilities are influenced by this level."
            >
              <NumberInput label="Level" {...form.getInputProps("level")} />
            </Tooltip>
            <Tooltip
              position="left"
              withArrow
              multiline
              width={220}
              label="Each combatant is a hero (player characters and their allies) or an enemy, determining which side they fight on when the sim runs. If a combatant's stats might be used on both sides, just make a copy with this value changed."
            >
              <Select
                withAsterisk
                required
                label="Hero or Enemy"
                placeholder="Select..."
                data={[
                  { value: "0", label: "Heroes" },
                  { value: "1", label: "Enemies" },
                ]}
                {...form.getInputProps("heroOrVillain")}
              />
            </Tooltip>
            <TextInput label="Character Type" {...form.getInputProps("characterType")} />
            <Divider label="Ability Scores" labelPosition="center" />
            <NumberInput label="Strength" {...form.getInputProps("strength")} />
            <NumberInput label="Dexterity" {...form.getInputProps("dexterity")} />
            <NumberInput label="Constitution" {...form.getInputProps("constitution")} />
            <NumberInput label="Intelligence" {...form.getInputProps("intelligence")} />
            <NumberInput label="Wisdom" {...form.getInputProps("wisdom")} />
            <NumberInput label="Charisma" {...form.getInputProps("charisma")} />
          </Card>

          <Card shadow="md" padding="md">
            <Title order={3}>Attacks & Positioning</Title>
            <Tooltip
              position="left"
              withArrow
              multiline
              width={220}
              label="This value is the total added to the d20 roll when rolling to hit (ability score + proficiency bonus, if relevant) with the combatant's weapon of choice. It does not include temporary buffs such as from spells or advantage gained in combat."
            >
              <NumberInput label="Attack Modifier" {...form.getInputProps("attackModifier")} />
            </Tooltip>
            <Tooltip
              position="left"
              withArrow
              multiline
              width={220}
              label="This value is a flat damage number that is applied when an attack hits with the combatant's weapon of choice. For example, if the combatant's longsword deals 1d8+5, this number should be entered as 9.5 - the average. This value does not include additional damage from situational abilities (Smite, Sneak Attack, spell buffs, etc.) - that is handled elsewhere."
            >
              <NumberInput label="Attack Damage" {...form.getInputProps("attackDamage")} />
            </Tooltip>
            <Tooltip
              position="left"
              withArrow
              multiline
              width={220}
              label="The number of attacks the combatant makes as part of their attack action or multiattack. Do not include offhand attack in this number."
            >
              <NumberInput label="# of Attacks" {...form.getInputProps("attackNumber")} />
            </Tooltip>
            <Tooltip
              position="left"
              withArrow
              multiline
              width={220}
              label="If a number other than 0 is given here, the combatant can use its bonus action to attack with its offhand, given it took the attack action already this turn. The to hit modifier is considered to be the same."
            >
              <NumberInput label="Offhand damage" {...form.getInputProps("offHandDamage")} />
            </Tooltip>
            <Checkbox label="Uses Range Attacks" {...form.getInputProps("usesRangeAttacks")} />
            <Select
              label="Position in feet"
              placeholder="Select position"
              data={["Front", "Middle", "Back"]}
              {...form.getInputProps("position")}
            />
            <Select
              label="Damage Type"
              placeholder="Select type"
              data={["slashing", "piercing", "bludgeoning"]}
              {...form.getInputProps("dmgType")}
            />
          </Card>

          <Card shadow="md" padding="md">
            <Title order={3}>Other</Title>
            <TextInput label="Other Abilities" {...form.getInputProps("otherAbilities")} />
            <Select
              label="Strategy Level"
              placeholder="Select level"
              data={["Level 2 - Beast", "Level 5 - Average Player", "Level 8 - Evil Wizard"]}
              {...form.getInputProps("strategyLevel")}
            />
          </Card>

          <Card shadow="sm" padding="md">
            <Title order={5}>Spellcasting</Title>
            <NumberInput label="Spell Mod" />
            <NumberInput label="Spell DC" />
            {/* Add inputs for spell slots or other spell-related attributes */}
          </Card>
        </SimpleGrid>

        <Group position="right" mt="md">
          <Button type="submit">Save Character</Button>
          <Button type="button">Load from Archive</Button>
          <Button type="button">Delete Character</Button>
          <Button type="button" color="red" onClick={() => setOpened(false)}>
            Cancel
          </Button>
        </Group>
      </form>
    </Modal>
  )
}

export default NewCombatantModal
