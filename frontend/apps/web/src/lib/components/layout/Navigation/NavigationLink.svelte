<script lang="ts">
  import type { Icon } from "@intric/icons";
  import { cva } from "class-variance-authority";

  export let href: string;
  export let isActive: boolean;
  export let icon: Icon;
  export let label: string;

  const link = cva(
    [
      "relative",
      "flex",
      "gap-4",
      "px-[1.45rem]",
      "py-2.5",
      "hover:font-medium",
      "hover:tracking-normal",
      "hover:text-primary"
    ],
    {
      variants: {
        active: {
          true: ["bg-hover-dimmer", "hover:bg-hover-default", "font-medium"],
          false: ["hover:bg-hover-dimmer", "tracking-[0.008rem]", "text-secondary"]
        }
      }
    }
  );
</script>

<a class={link({ active: isActive })} aria-current={isActive ? "page" : undefined} {href}>
  {#if isActive}
    <div class="bg-dynamic-default absolute top-0 bottom-0 left-0 w-[4px] rounded-r-full"></div>
  {/if}
  <svelte:component this={icon} class="size-6" />
  <span>{label}</span>
  <slot />
</a>
