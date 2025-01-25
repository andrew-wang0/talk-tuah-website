import { cn } from "@/lib/cn";

type ChatMessageProps = {
    message: string;
    accentColor: string;
    name: string;
    isSelf: boolean;
    hideName?: boolean;
};

export const ChatMessage = ({
    name,
    message,
    accentColor,
    isSelf,
    hideName,
}: ChatMessageProps) => {
    return (
        <div className={`flex flex-col gap-0 ${hideName ? "pt-0" : "pt-6"}`}>
            {!hideName && (
                <div
                    className={`text-${
                        isSelf
                            ? "gray-700"
                            : accentColor + "-800 text-ts-" + accentColor
                    } uppercase text-base`}
                >
                    {name}
                </div>
            )}
            <div
                className={cn(
                    "pr-4 text-lg leading-snug whitespace-pre-line",
                    isSelf
                        ? "text-gray-800"
                        : // : `text-${accentColor}-500 drop-shadow-${accentColor}`
                          `text-${accentColor}-500`
                )}
            >
                {message}
            </div>
        </div>
    );
};
