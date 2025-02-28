import { Button } from "@/components/button/Button";
import { LoadingSVG } from "@/components/button/LoadingSVG";
import { SettingsDropdown } from "@/components/playground/SettingsDropdown";
import { useConfig } from "@/hooks/useConfig";
import { ConnectionState } from "livekit-client";
import { ReactNode } from "react";
import { MessageSquareHeartIcon } from "lucide-react";

type PlaygroundHeader = {
    logo?: ReactNode;
    title?: ReactNode;
    githubLink?: string;
    height: number;
    accentColor: string;
    connectionState: ConnectionState;
    onConnectClicked: () => void;
};

export const PlaygroundHeader = ({
    logo,
    title,
    githubLink,
    accentColor,
    height,
    onConnectClicked,
    connectionState,
}: PlaygroundHeader) => {
    const { config } = useConfig();
    return (
        <div
            className={`flex gap-4 pt-4 text-${accentColor}-500 justify-between items-center shrink-0`}
            style={{
                height: height + "px",
            }}
        >
            <div className="flex items-center gap-3 basis-2/3">
                <div className="flex lg:basis-1/2">
                    <a href="https://livekit.io">
                        {logo ?? (
                                <svg
                                    width="36"
                                    height="36"
                                    viewBox="0 0 59 59"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <rect
                                        width="59"
                                        height="59"
                                        rx="10"
                                        fill="#5797FF"
                                    />
                                    <path
                                        d="M43.3333 30.3332V33.1667C43.3333 38.4167 40.3333 40.6667 35.8333 40.6667H20.8333C16.3333 40.6667 13.3333 38.4167 13.3333 33.1667V24.1666C13.3333 18.9166 16.3333 16.6666 20.8333 16.6666H25.3333C25.1166 17.3 24.9999 18 24.9999 18.75V25.25C24.9999 26.8667 25.5333 28.2333 26.4833 29.1833C27.4333 30.1333 28.7999 30.6667 30.4166 30.6667V32.9834C30.4166 33.8334 31.3833 34.3499 32.0999 33.8832L36.9166 30.6667H41.2499C41.9999 30.6667 42.6999 30.5499 43.3333 30.3332Z"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-miterlimit="10"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M46.6667 18.75V25.2501C46.6667 27.7334 45.4 29.6 43.3333 30.3333C42.7 30.55 42 30.6667 41.25 30.6667H36.9167L32.1 33.8833C31.3833 34.35 30.4167 33.8334 30.4167 32.9834V30.6667C28.8 30.6667 27.4333 30.1334 26.4833 29.1834C25.5333 28.2334 25 26.8667 25 25.2501V18.75C25 18 25.1167 17.3 25.3333 16.6667C26.0667 14.6 27.9333 13.3334 30.4167 13.3334H41.25C44.5 13.3334 46.6667 15.5 46.6667 18.75Z"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-miterlimit="10"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M22.3335 46.6666H34.3335"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-miterlimit="10"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M28.3333 40.6667V46.6667"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-miterlimit="10"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M40.8258 22.0833H40.8408"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M36.1596 22.0833H36.1746"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M31.4923 22.0833H31.5073"
                                        stroke="white"
                                        stroke-width="2.5"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                </svg>
                            ) ?? <LKLogo />}
                    </a>
                </div>
                <div className="lg:basis-1/2 lg:text-center text-lg lg:text-lg font-semibold text-gray-800">
                    {title}
                </div>
            </div>
            <div className="flex basis-1/3 justify-end items-center gap-2">
                {/* {githubLink && (
                    <a
                        href={githubLink}
                        target="_blank"
                        className={`text-white hover:text-white/80`}
                    >
                        <GithubSVG />
                    </a>
                )} */}
                {config.settings.editable && <SettingsDropdown />}
                <Button
                    accentColor={
                        connectionState === ConnectionState.Connected
                            ? "red"
                            : accentColor
                    }
                    disabled={connectionState === ConnectionState.Connecting}
                    onClick={() => {
                        onConnectClicked();
                    }}
                    className="h-9 items-center flex text-gray-200"
                >
                    {connectionState === ConnectionState.Connecting ? (
                        <LoadingSVG />
                    ) : connectionState === ConnectionState.Connected ? (
                        "Disconnect"
                    ) : (
                        "Connect"
                    )}
                </Button>
            </div>
        </div>
    );
};

const LKLogo = () => (
    <svg
        width="28"
        height="28"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
    >
        <g clipPath="url(#clip0_101_119699)">
            <path
                d="M19.2006 12.7998H12.7996V19.2008H19.2006V12.7998Z"
                fill="currentColor"
            />
            <path
                d="M25.6014 6.40137H19.2004V12.8024H25.6014V6.40137Z"
                fill="currentColor"
            />
            <path
                d="M25.6014 19.2002H19.2004V25.6012H25.6014V19.2002Z"
                fill="currentColor"
            />
            <path d="M32 0H25.599V6.401H32V0Z" fill="currentColor" />
            <path
                d="M32 25.5986H25.599V31.9996H32V25.5986Z"
                fill="currentColor"
            />
            <path
                d="M6.401 25.599V19.2005V12.7995V6.401V0H0V6.401V12.7995V19.2005V25.599V32H6.401H12.7995H19.2005V25.599H12.7995H6.401Z"
                fill="white"
            />
        </g>
        <defs>
            <clipPath id="clip0_101_119699">
                <rect width="32" height="32" fill="white" />
            </clipPath>
        </defs>
    </svg>
);

const GithubSVG = () => (
    <svg
        width="24"
        height="24"
        viewBox="0 0 98 96"
        xmlns="http://www.w3.org/2000/svg"
    >
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z"
            fill="currentColor"
        />
    </svg>
);
