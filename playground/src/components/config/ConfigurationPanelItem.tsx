import { ReactNode } from "react";
import { PlaygroundDeviceSelector } from "@/components/playground/PlaygroundDeviceSelector";
import { TrackToggle } from "@livekit/components-react";
import { Track } from "livekit-client";

type ConfigurationPanelItemProps = {
    title: string;
    children?: ReactNode;
    deviceSelectorKind?: MediaDeviceKind;
};

export const ConfigurationPanelItem: React.FC<ConfigurationPanelItemProps> = ({
    children,
    title,
    deviceSelectorKind,
}) => {
    return (
        <div className="w-full text-gray-500 py-4 border-b border-b-gray-500 relative">
            <div className="flex flex-row justify-between items-center px-4 text-xs uppercase tracking-wider">
                <h3>{title}</h3>
                {deviceSelectorKind && (
                    <span className="flex flex-row gap-2">
                        <TrackToggle
                            className="px-2 py-1 bg-gray-200 text-gray-500 border border-gray-500 rounded-sm hover:bg-gray-300/80"
                            source={
                                deviceSelectorKind === "audioinput"
                                    ? Track.Source.Microphone
                                    : Track.Source.Camera
                            }
                        />
                        <PlaygroundDeviceSelector kind={deviceSelectorKind} />
                    </span>
                )}
            </div>
            <div className="px-4 py-2 text-xs text-gray-500 leading-normal">
                {children}
            </div>
        </div>
    );
};
