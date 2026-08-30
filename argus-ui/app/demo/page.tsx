import { SplineSceneBasic } from "@/components/demo/spline-scene";

export default function DemoPage() {
    return (
        <div className="min-h-screen bg-black flex items-center justify-center p-8">
            <div className="w-full max-w-6xl">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-white mb-2">Component Integration Demo</h1>
                    <p className="text-zinc-400">Spline 3D Scene + Spotlight + Shadcn Card</p>
                </div>
                <SplineSceneBasic />
            </div>
        </div>
    )
}
