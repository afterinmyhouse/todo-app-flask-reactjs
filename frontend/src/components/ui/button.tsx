import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

// Centralized styling API for buttons.
// `cva` gives us a typed set of "variants" (visual style) and "size" options while keeping
// the base class list in one place.
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline:
          "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ComponentPropsWithoutRef<"button">,
    VariantProps<typeof buttonVariants> {
  // When true, the Button renders a Radix `Slot` so the *child* becomes the underlying element.
  // This is useful to style links/other components as buttons, but it changes element semantics.
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      disabled,
      onClick,
      tabIndex,
      ...props
    },
    ref,
  ) => {
    // `Slot` forwards props to the child element; otherwise render a native `<button>`.
    const Comp = asChild ? Slot : "button";

    // When `asChild` is used, `disabled` is not a native concept for most elements.
    // We add minimal semantics and prevent clicks to match user expectations.
    const composedOnClick: React.MouseEventHandler<HTMLElement> = (event) => {
      if (asChild && disabled) {
        event.preventDefault();
        event.stopPropagation();
        return;
      }

      onClick?.(event as unknown as React.MouseEvent<HTMLButtonElement>);
    };

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        // With `asChild`, the underlying element may not be a <button>. We keep the public ref
        // type ergonomic for the common case and cast for Slot compatibility.
        ref={ref as any}
        // Make "disabled" discoverable for assistive tech and styling when the element isn't a <button>.
        aria-disabled={asChild && disabled ? true : undefined}
        data-disabled={asChild && disabled ? "" : undefined}
        tabIndex={asChild && disabled ? -1 : tabIndex}
        onClick={composedOnClick}
        // Only pass the native `disabled` attribute to real <button> elements.
        disabled={asChild ? undefined : disabled}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
