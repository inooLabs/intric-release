<script lang="ts">
  import type { GroupChatSparse } from "@intric/intric-js";
  import { IconEdit } from "@intric/icons/edit";
  import { IconTrash } from "@intric/icons/trash";
  import { IconEllipsis } from "@intric/icons/ellipsis";
  import { Button, Dialog, Dropdown } from "@intric/ui";
  import { getIntric } from "$lib/core/Intric";
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import { writable } from "svelte/store";
  import PublishingDialog from "$lib/features/publishing/components/PublishingDialog.svelte";
  import { IconArrowUpToLine } from "@intric/icons/arrow-up-to-line";
  import { IconArrowDownToLine } from "@intric/icons/arrow-down-to-line";
  import { createAsyncState } from "$lib/core/helpers/createAsyncState.svelte";

  export let groupChat: GroupChatSparse;

  const {
    state: { currentSpace },
    refreshCurrentSpace
  } = getSpacesManager();

  const intric = getIntric();

  const deleteGroupChat = createAsyncState(async () => {
    try {
      await intric.groupChats.delete(groupChat);
      refreshCurrentSpace("applications");
      $showDeleteDialog = false;
    } catch (e) {
      alert("Could not delete groupChat.");
      console.error(e);
    }
  });

  let showDeleteDialog: Dialog.OpenState;
  const showPublishDialog = writable(false);

  let showActions = (["edit", "publish", "delete"] as const).some((permission) =>
    groupChat.permissions?.includes(permission)
  );
</script>

{#if showActions}
  <Dropdown.Root>
    <Dropdown.Trigger let:trigger asFragment>
      <Button variant="on-fill" is={trigger} disabled={false} padding="icon">
        <IconEllipsis />
      </Button>
    </Dropdown.Trigger>
    <Dropdown.Menu let:item>
      {#if groupChat.permissions?.includes("edit")}
        <Button
          is={item}
          href="/spaces/{$currentSpace.routeId}/group-chats/{groupChat.id}/edit"
          padding="icon-leading"
        >
          <IconEdit size="sm" />
          Edit</Button
        >
      {/if}
      {#if groupChat.permissions?.includes("publish")}
        <Button
          is={item}
          on:click={() => {
            $showPublishDialog = true;
          }}
          padding="icon-leading"
        >
          {#if groupChat.published}
            <IconArrowDownToLine size="sm"></IconArrowDownToLine>
            Unpublish
          {:else}
            <IconArrowUpToLine size="sm"></IconArrowUpToLine>
            Publish
          {/if}
        </Button>
      {/if}
      {#if groupChat.permissions?.includes("delete")}
        <Button
          is={item}
          variant="destructive"
          on:click={() => {
            $showDeleteDialog = true;
          }}
          padding="icon-leading"
        >
          <IconTrash size="sm" />Delete</Button
        >
      {/if}
    </Dropdown.Menu>
  </Dropdown.Root>
{/if}

<Dialog.Root alert bind:isOpen={showDeleteDialog}>
  <Dialog.Content width="small">
    <Dialog.Title>Delete groupChat</Dialog.Title>
    <Dialog.Description
      >Do you really want to delete <span class="italic">{groupChat.name}</span
      >?</Dialog.Description
    >

    <Dialog.Controls let:close>
      <Button is={close}>Cancel</Button>
      <Button variant="destructive" on:click={deleteGroupChat}
        >{deleteGroupChat.isLoading ? "Deleting..." : "Delete"}</Button
      >
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>

<PublishingDialog
  resource={groupChat}
  endpoints={intric.assistants}
  openController={showPublishDialog}
  awaitUpdate
></PublishingDialog>
