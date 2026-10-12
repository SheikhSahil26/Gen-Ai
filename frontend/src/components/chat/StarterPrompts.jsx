import { ArrowUpRight, Gift, Search, SlidersHorizontal } from "lucide-react"

const prompts = [
  { icon: Gift, label: "Find a gift", prompt: "Help me find a thoughtful gift under ₹5,000" },
  { icon: Search, label: "Explore the catalog", prompt: "List me the products" },
  { icon: SlidersHorizontal, label: "Compare products", prompt: "Can you help me compare a few products?" },
]

export function StarterPrompts({ onChoose }) {
  return <section className="starter-prompts"><div className="section-kicker">A GOOD PLACE TO START</div><div className="prompt-grid">
    {prompts.map(({ icon: Icon, label, prompt }) => <button className="prompt-card" key={label} onClick={() => onChoose(prompt)}><span className="prompt-icon"><Icon size={16}/></span><span>{label}</span><ArrowUpRight size={15} className="prompt-arrow"/></button>)}
  </div></section>
}
