declare module 'lucide-react' {
    import type { ComponentType, SVGProps } from 'react';
    type IconProps = SVGProps<SVGSVGElement> & { size?: number | string };
    export const ArrowRight: ComponentType<IconProps>;
    export const ArrowUpRight: ComponentType<IconProps>;
    export const LoaderCircle: ComponentType<IconProps>;
    export const ShieldCheck: ComponentType<IconProps>;
    export const Shield: ComponentType<IconProps>;
    export const ShieldAlert: ComponentType<IconProps>;
    export const Radio: ComponentType<IconProps>;
    export const Braces: ComponentType<IconProps>;
    export const RefreshCw: ComponentType<IconProps>;
    export const History: ComponentType<IconProps>;
    export const Puzzle: ComponentType<IconProps>;
    export const LogOut: ComponentType<IconProps>;
    export const ExternalLink: ComponentType<IconProps>;
}
