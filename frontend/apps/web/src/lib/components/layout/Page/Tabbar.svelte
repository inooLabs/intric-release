<script lang="ts">
  import { getContentTabs } from "./ctx";

  const {
    elements: { list }
  } = getContentTabs();
</script>

<div
  {...$list}
  use:list
  class="text-primary left-[50%] flex flex-grow items-center justify-center gap-2 pr-3 lg:absolute lg:-translate-x-[50%]"
  aria-label="Main views available for the current resource/site"
>
  <slot />
</div>
