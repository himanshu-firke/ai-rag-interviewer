import HeroSection from "@/components/ui/hero-01-utils/hero";
import Header from "@/components/ui/hero-01-utils/header";
import BrandSlider from "@/components/ui/hero-01-utils/brand-slider";

export default function AgencyHeroSection() {
  const avatarList = [
    {
      image:
        "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
    },
    {
      image:
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face",
    },
    {
      image:
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    },
    {
      image:
        "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face",
    },
  ];

  const navigationData = [
    { title: "Home", href: "#", isActive: true },
    { title: "Features", href: "#features" },
    { title: "How It Works", href: "#how-it-works" },
    { title: "Pricing", href: "#pricing" },
    { title: "Contact", href: "#contact" },
  ];

  const brandList = [
    { name: "Python", image: null },
    { name: "FastAPI", image: null },
    { name: "OpenAI GPT-4", image: null },
    { name: "LangChain", image: null },
    { name: "PostgreSQL", image: null },
    { name: "Next.js", image: null },
    { name: "Whisper AI", image: null },
    { name: "RAG Pipeline", image: null },
  ];

  return (
    <div className="relative">
      <Header navigationData={navigationData} />
      <main>
        <HeroSection avatarList={avatarList} />
        <BrandSlider brandList={brandList} />
      </main>
    </div>
  );
}
