# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides an interface for REST API implementations to follow."""

from __future__ import annotations

__all__: typing.Sequence[str] = ("RESTClient", "TokenStrategy")

import abc
import datetime
import typing

from hikari import permissions as permissions_
from hikari import scheduled_events
from hikari import traits
from hikari import undefined

if typing.TYPE_CHECKING:
    from hikari import applications
    from hikari import audit_logs
    from hikari import auto_mod
    from hikari import channels as channels_
    from hikari import colors
    from hikari import commands
    from hikari import embeds as embeds_
    from hikari import emojis
    from hikari import files
    from hikari import guilds
    from hikari import invites
    from hikari import iterators
    from hikari import locales
    from hikari import messages as messages_
    from hikari import monetization
    from hikari import sessions
    from hikari import snowflakes
    from hikari import stage_instances
    from hikari import stickers as stickers_
    from hikari import templates
    from hikari import users
    from hikari import voices
    from hikari import webhooks
    from hikari.api import entity_factory as entity_factory_
    from hikari.api import special_endpoints
    from hikari.interactions import base_interactions
    from hikari.internal import time


class TokenStrategy(abc.ABC):
    """Interface of an object used for managing OAuth2 access."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def token_type(self) -> applications.TokenType | str:
        """Type of token this strategy returns."""

    @abc.abstractmethod
    async def acquire(self, client: RESTClient) -> str:
        """Acquire an authorization token (including the prefix).

        Parameters
        ----------
        client
            The rest client to use to acquire the token.

        Returns
        -------
        str
            The current authorization token to use for this client and it's
            prefix.
        """

    @abc.abstractmethod
    def invalidate(self, token: str | None) -> None:
        """Invalidate the cached token in this handler.

        !!! note
            [`token`][] may be provided in-order to avoid newly generated tokens
            from being invalidated due to multiple calls being made by separate
            subroutines which are handling the same token.

        Parameters
        ----------
        token
            The token to specifically invalidate. If provided then this will only
            invalidate the cached token if it matches this, otherwise it'll be
            invalidated regardless.
        """


class RESTClient(traits.NetworkSettingsAware, abc.ABC):
    """Interface for functionality that a REST API implementation provides."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        """Whether this component is alive."""

    @property
    @abc.abstractmethod
    def entity_factory(self) -> entity_factory_.EntityFactory:
        """Entity factory used by this REST client."""

    @property
    @abc.abstractmethod
    def token_type(self) -> str | applications.TokenType | None:
        """Type of token this client is using for most requests.

        If this is [`None`][] then this client will likely only work
        for some endpoints such as public and webhook ones.
        """

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the client session."""

    @abc.abstractmethod
    async def fetch_channel(
        self, channel: snowflakes.SnowflakeishOr[channels_.PartialChannel]
    ) -> channels_.PartialChannel:
        """Fetch a channel.

        Parameters
        ----------
        channel
            The channel to fetch. This may be the object or the ID of an
            existing channel.

        Returns
        -------
        hikari.channels.PartialChannel
            The channel. This will be a _derivative_ of
            [`hikari.channels.PartialChannel`][], depending on the type of
            channel you request for.

            This means that you may get one of
            [`hikari.channels.DMChannel`][],
            [`hikari.channels.GroupDMChannel`][],
            [`hikari.channels.GuildTextChannel`][],
            [`hikari.channels.GuildVoiceChannel`][],
            [`hikari.channels.GuildNewsChannel`][].

            Likewise, the [`hikari.channels.GuildChannel`][] can be used to
            determine if a channel is guild-bound, and
            [`hikari.channels.TextableChannel`][] can be used to determine
            if the channel provides textual functionality to the application.

            You can check for these using the [`isinstance`][]
            builtin function.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.VIEW_CHANNEL`][] permission in the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_channel(  # noqa: PLR0913 - Too many arguments
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
        /,
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        flags: undefined.UndefinedOr[channels_.ChannelFlag] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        video_quality_mode: undefined.UndefinedOr[channels_.VideoQualityMode | int] = undefined.UNDEFINED,
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        region: undefined.UndefinedNoneOr[voices.VoiceRegion | str] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        parent_category: undefined.UndefinedOr[
            snowflakes.SnowflakeishOr[channels_.GuildCategory]
        ] = undefined.UNDEFINED,
        default_auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_thread_rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_forum_layout: undefined.UndefinedOr[channels_.ForumLayoutType | int] = undefined.UNDEFINED,
        default_sort_order: undefined.UndefinedOr[channels_.ForumSortOrderType | int] = undefined.UNDEFINED,
        available_tags: undefined.UndefinedOr[typing.Sequence[channels_.ForumTag]] = undefined.UNDEFINED,
        default_reaction_emoji: str
        | emojis.Emoji
        | undefined.UndefinedType
        | snowflakes.Snowflake
        | None = undefined.UNDEFINED,
        archived: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        locked: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        invitable: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        applied_tags: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[channels_.ForumTag]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.PartialChannel:
        """Edit a channel.

        Parameters
        ----------
        channel
            The channel to edit. This may be the object or the ID of an
            existing channel.
        name
            If provided, the new name for the channel.
        flags
            If provided, the new channel flags to use for the channel. This can
            only be used on a forum or media channel to apply [`hikari.channels.ChannelFlag.REQUIRE_TAG`][], or
            on a forum or media thread to apply [`hikari.channels.ChannelFlag.PINNED`][].
        position
            If provided, the new position for the channel.
        topic
            If provided, the new topic for the channel.
        nsfw
            If provided, whether the channel should be marked as NSFW or not.
        bitrate
            If provided, the new bitrate for the channel.
        video_quality_mode
            If provided, the new video quality mode for the channel.
        user_limit
            If provided, the new user limit in the channel.
        rate_limit_per_user
            If provided, the new rate limit per user in the channel.
        region
            If provided, the voice region to set for this channel. Passing
            [`None`][] here will set it to "auto" mode where the used
            region will be decided based on the first person who connects to it
            when it's empty.
        permission_overwrites
            If provided, the new permission overwrites for the channel.
        parent_category
            If provided, the new guild category for the channel.
        default_auto_archive_duration
            If provided, the auto archive duration Discord's end user client
            should default to when creating threads in this channel.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        default_thread_rate_limit_per_user
            If provided, the ratelimit that should be set in threads derived
            from this channel.

            This only applies to forum and media channels.
        default_forum_layout
            If provided, the default forum layout to show in the client.
        default_sort_order
            If provided, the default sort order to show in the client.
        available_tags
            If provided, the new available tags to select from when creating a thread.

            This only applies to forum and media channels.
        default_reaction_emoji
            If provided, the new default reaction emoji for threads created in a forum or media channel.

            This only applies to forum and media channels.
        archived
            If provided, the new archived state for the thread. This only
            applies to threads.
        locked
            If provided, the new locked state for the thread. This only applies
            to threads.

            If it's locked then only people with [`hikari.permissions.Permissions.MANAGE_THREADS`][] can unarchive it.
        invitable
            If provided, the new setting for whether non-moderators can invite
            new members to a private thread. This only applies to threads.
        auto_archive_duration
            If provided, the new auto archive duration for this thread. This
            only applies to threads.

            This should be either 60, 1440, 4320 or 10080 minutes, as of
            writing.
        applied_tags
            If provided, the new tags to apply to the thread. This only applies
            to threads in a forum or media channel.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.PartialChannel
            The edited channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing permissions to edit the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def follow_channel(
        self,
        news_channel: snowflakes.SnowflakeishOr[channels_.GuildNewsChannel],
        target_channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
    ) -> channels_.ChannelFollow:
        """Follow a news channel to send messages to a target channel.

        Parameters
        ----------
        news_channel
            The object or ID of the news channel to follow.
        target_channel
            The object or ID of the channel to target.

        Returns
        -------
        hikari.channels.ChannelFollow
            Information about the new relationship that was made.

        Raises
        ------
        hikari.errors.BadRequestError
            If you try to follow a channel that's not a news channel or if the
            target channel has reached it's webhook limit, which is 10 at the
            time of writing.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission in the target
            channel or are missing the [`hikari.permissions.Permissions.VIEW_CHANNEL`][] permission in the origin
            channel.
        hikari.errors.NotFoundError
            If the origin or target channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_channel(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PartialChannel],
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.PartialChannel:
        """Delete a channel in a guild, or close a DM.

        !!! note
            For Public servers, the set 'Rules' or 'Guidelines' channels and the
            'Public Server Updates' channel cannot be deleted.

        Parameters
        ----------
        channel
            The channel to delete. This may be the object or the ID of an
            existing channel.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.PartialChannel
            Object of the channel that was deleted.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission in the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_my_voice_state(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> voices.VoiceState:
        """Fetch the current user's voice state.

        Parameters
        ----------
        guild
            The guild to fetch the state from. This may be the object or the ID.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel, message or voice state is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.

        Returns
        -------
        voices.VoiceState
            The current user's voice state.
        """

    @abc.abstractmethod
    async def fetch_voice_state(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], user: snowflakes.SnowflakeishOr[users.PartialUser]
    ) -> voices.VoiceState:
        """Fetch the current user's voice state.

        Parameters
        ----------
        guild
            The guild to fetch the state from. This may be the object or the ID.
        user
            The user to fetch the state for. This may be the object or the ID.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel, message or voice state is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.

        Returns
        -------
        voices.VoiceState
            The user's voice state.
        """

    @abc.abstractmethod
    async def edit_my_voice_state(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        channel: snowflakes.SnowflakeishOr[channels_.GuildStageChannel],
        *,
        suppress: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        request_to_speak: undefined.UndefinedType | bool | datetime.datetime = undefined.UNDEFINED,
    ) -> None:
        """Edit the current user's voice state in a stage channel.

        !!! note
            The current user has to have already joined the target stage channel
            before any calls can be made to this endpoint.

        Parameters
        ----------
        guild
            Object or Id of the guild to edit a voice state in.
        channel
            Object or Id of the channel to edit a voice state in.
        suppress
            If specified, whether the user should be allowed to become a speaker
            in the target stage channel with [`True`][] suppressing them from
            becoming one.
        request_to_speak
            Whether to request to speak. This may be one of the following:

            * [`True`][] to indicate that the bot wants to speak.
            * [`False`][] to remove any previously set request to speak.
            * [`datetime.datetime`][] to specify when they want their request to
                speak timestamp to be set to. If a datetime from the past is
                passed then Discord will use the current time instead.

        Raises
        ------
        hikari.errors.BadRequestError
            If you try to target a non-staging channel.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MUTE_MEMBERS`][] permission in the channel.
        hikari.errors.NotFoundError
            If the channel, message or voice state is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_voice_state(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        channel: snowflakes.SnowflakeishOr[channels_.GuildStageChannel],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        suppress: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> None:
        """Edit an existing voice state in a stage channel.

        !!! note
            The target user must already be present in the stage channel before
            any calls are made to this endpoint.

        Parameters
        ----------
        guild
            Object or ID of the guild to edit a voice state in.
        channel
            Object or ID of the channel to edit a voice state in.
        user
            Object or ID of the user to edit the voice state of.
        suppress
            If defined, whether the user should be allowed to become a speaker
            in the target stage channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If you try to target a non-staging channel.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MUTE_MEMBERS`][] permission in the channel.
        hikari.errors.NotFoundError
            If the channel, message or voice state is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @typing.overload
    @abc.abstractmethod
    async def edit_permission_overwrite(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
        target: channels_.PermissionOverwrite | users.PartialUser | guilds.PartialRole,
        *,
        allow: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        deny: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        # Edit permissions for a target entity
        ...

    @typing.overload
    @abc.abstractmethod
    async def edit_permission_overwrite(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
        target: snowflakes.Snowflakeish,
        *,
        target_type: channels_.PermissionOverwriteType | int,
        allow: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        deny: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        # Edit permissions for a given entity ID and type
        ...

    @abc.abstractmethod
    async def edit_permission_overwrite(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
        target: snowflakes.Snowflakeish | users.PartialUser | guilds.PartialRole | channels_.PermissionOverwrite,
        *,
        target_type: undefined.UndefinedOr[channels_.PermissionOverwriteType | int] = undefined.UNDEFINED,
        allow: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        deny: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Edit permissions for a specific entity in the given guild channel.

        Parameters
        ----------
        channel
            The channel to edit a permission overwrite in. This may be the
            object, or the ID of an existing channel.
        target
            The channel overwrite to edit. This may be the object or the ID of an
            existing overwrite.
        target_type
            If provided, the type of the target to update. If unset, will attempt to get
            the type from `target`.
        allow
            If provided, the new value of all allowed permissions.
        deny
            If provided, the new value of all disallowed permissions.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        TypeError
            If `target_type` is unset and we were unable to determine the type
            from `target`.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`MANAGE_PERMISSIONS`][hikari.permissions.Permissions.MANAGE_ROLES]
            permission in the channel.
        hikari.errors.NotFoundError
            If the channel is not found or the target is not found if it is
            a role.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_permission_overwrite(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
        target: channels_.PermissionOverwrite | guilds.PartialRole | users.PartialUser | snowflakes.Snowflakeish,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete a custom permission for an entity in a given guild channel.

        Parameters
        ----------
        channel
            The channel to delete a permission overwrite in. This may be the
            object, or the ID of an existing channel.
        target
            The channel overwrite to delete.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`MANAGE_PERMISSIONS`][hikari.permissions.Permissions.MANAGE_ROLES]
            permission in the channel.
        hikari.errors.NotFoundError
            If the channel is not found or the target is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_channel_invites(
        self, channel: snowflakes.SnowflakeishOr[channels_.GuildChannel]
    ) -> typing.Sequence[invites.InviteWithMetadata]:
        """Fetch all invites pointing to the given guild channel.

        Parameters
        ----------
        channel
            The channel to fetch the invites from. This may be a channel
            object, or the ID of an existing channel.

        Returns
        -------
        typing.Sequence[hikari.invites.InviteWithMetadata]
            The invites pointing to the given guild channel.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission in the channel.
        hikari.errors.NotFoundError
            If the channel is not found in any guilds you are a member of.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_invite(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildChannel],
        *,
        max_age: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        max_uses: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        temporary: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        unique: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        target_type: undefined.UndefinedOr[invites.TargetType] = undefined.UNDEFINED,
        target_user: undefined.UndefinedOr[snowflakes.SnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
        target_application: undefined.UndefinedOr[
            snowflakes.SnowflakeishOr[guilds.PartialApplication]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> invites.InviteWithMetadata:
        """Create an invite to the given guild channel.

        Parameters
        ----------
        channel
            The channel to create a invite for. This may be the object
            or the ID of an existing channel.
        max_age
            If provided, the duration of the invite before expiry.
        max_uses
            If provided, the max uses the invite can have.
        temporary
            If provided, whether the invite only grants temporary membership.
        unique
            If provided, whether the invite should be unique.
        target_type
            If provided, the target type of this invite.
        target_user
            If provided, the target user id for this invite. This may be the
            object or the ID of an existing user.

            !!! note
                This is required if `target_type` is [`hikari.invites.TargetType.STREAM`][] and the targeted
                user must be streaming into the channel.
        target_application
            If provided, the target application id for this invite. This may be
            the object or the ID of an existing application.

            !!! note
                This is required if `target_type` is [`hikari.invites.TargetType.EMBEDDED_APPLICATION`][] and
                the targeted application must have the [`hikari.applications.ApplicationFlags.EMBEDDED`][] flag.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.invites.InviteWithMetadata
            The invite to the given guild channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.NotFoundError
            If the channel is not found, or if the target user does not exist,
            if provided.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def trigger_typing(
        self, channel: snowflakes.SnowflakeishOr[channels_.TextableChannel]
    ) -> special_endpoints.TypingIndicator:
        """Trigger typing in a text channel.

        !!! note
            The result of this call can be awaited to trigger typing once, or
            can be used as an async context manager to continually type until the
            context manager is left. Any errors documented below will happen then.

        Examples
        --------
        ```py
        # Trigger typing just once.
        await rest.trigger_typing(channel)

        # Trigger typing repeatedly for 1 minute.
        async with rest.trigger_typing(channel):
            await asyncio.sleep(60)
        ```

        !!! warning
            Sending a message to the channel will cause the typing indicator
            to disappear until it is re-triggered.

        Parameters
        ----------
        channel
            The channel to trigger typing in. This may be the object or
            the ID of an existing channel.

        Returns
        -------
        hikari.api.special_endpoints.TypingIndicator
            A typing indicator to use.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.SEND_MESSAGES`][] in the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_pins(
        self, channel: snowflakes.SnowflakeishOr[channels_.TextableChannel]
    ) -> typing.Sequence[messages_.Message]:
        """Fetch the pinned messages in this text channel.

        Parameters
        ----------
        channel
            The channel to fetch pins from. This may be the object or
            the ID of an existing channel.

        Returns
        -------
        typing.Sequence[hikari.messages.Message]
            The pinned messages in this text channel.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.VIEW_CHANNEL`][] in the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def pin_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
    ) -> None:
        """Pin an existing message in the given text channel.

        Parameters
        ----------
        channel
            The channel to pin a message in. This may be the object or
            the ID of an existing channel.
        message
            The message to pin. This may be the object or the ID
            of an existing message.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] in the channel.
        hikari.errors.NotFoundError
            If the channel is not found, or if the message does not exist in
            the given channel.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def unpin_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
    ) -> None:
        """Unpin a given message from a given text channel.

        Parameters
        ----------
        channel
            The channel to unpin a message in. This may be the object or
            the ID of an existing channel.
        message
            The message to unpin. This may be the object or the ID of an
            existing message.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] permission.
        hikari.errors.NotFoundError
            If the channel is not found or the message is not a pinned message
            in the given channel.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_messages(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        *,
        before: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[snowflakes.Unique]] = undefined.UNDEFINED,
        after: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[snowflakes.Unique]] = undefined.UNDEFINED,
        around: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[snowflakes.Unique]] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[messages_.Message]:
        """Browse the message history for a given text channel.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it,
            thus any errors documented below will happen then.

            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        channel
            The channel to fetch messages in. This may be the object or
            the ID of an existing channel.
        before
            If provided, fetch messages before this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may be any other Discord entity that has an ID. In this case, the
            date the object was first created will be used.
        after
            If provided, fetch messages after this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may be any other Discord entity that has an ID. In this case, the
            date the object was first created will be used.
        around
            If provided, fetch messages around this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may be any other Discord entity that has an ID. In this case, the
            date the object was first created will be used.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.messages.Message]
            An iterator to fetch the messages.

        Raises
        ------
        TypeError
            If you specify more than one of `before`, `after`, `about`.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.READ_MESSAGE_HISTORY`][] in the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
    ) -> messages_.Message:
        """Fetch a specific message in the given text channel.

        Parameters
        ----------
        channel
            The channel to fetch messages in. This may be the object or
            the ID of an existing channel.
        message
            The message to fetch. This may be the object or the ID of an
            existing message.

        Returns
        -------
        hikari.messages.Message
            The requested message.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.READ_MESSAGE_HISTORY`][] in the channel.
        hikari.errors.NotFoundError
            If the channel is not found or the message is not found in the
            given text channel.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        content: undefined.UndefinedOr[typing.Any] = undefined.UNDEFINED,
        *,
        attachment: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        attachments: undefined.UndefinedOr[typing.Sequence[files.Resourceish]] = undefined.UNDEFINED,
        component: undefined.UndefinedOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedOr[typing.Sequence[special_endpoints.ComponentBuilder]] = undefined.UNDEFINED,
        embed: undefined.UndefinedOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        poll: undefined.UndefinedOr[special_endpoints.PollBuilder] = undefined.UNDEFINED,
        sticker: undefined.UndefinedOr[snowflakes.SnowflakeishOr[stickers_.PartialSticker]] = undefined.UNDEFINED,
        stickers: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[stickers_.PartialSticker]
        ] = undefined.UNDEFINED,
        tts: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        reply: undefined.UndefinedOr[snowflakes.SnowflakeishOr[messages_.PartialMessage]] = undefined.UNDEFINED,
        reply_must_exist: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_reply: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
        flags: undefined.UndefinedType | int | messages_.MessageFlag = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Create a message in the given channel.

        Parameters
        ----------
        channel
            The channel to create the message in.
        content
            If provided, the message contents. If
            [`hikari.undefined.UNDEFINED`][], then nothing will be sent
            in the content. Any other value here will be cast to a
            [`str`][].

            If this is a [`hikari.embeds.Embed`][] and no `embed` nor `embeds` kwarg
            is provided, then this will instead update the embed. This allows
            for simpler syntax when sending an embed alone.

            Likewise, if this is a [`hikari.files.Resource`][], then the
            content is instead treated as an attachment if no `attachment` and
            no `attachments` kwargs are provided.
        attachment
            If provided, the message attachment. This can be a resource,
            or string of a path on your computer or a URL.

            Attachments can be passed as many different things, to aid in
            convenience.

            - If a [`pathlib.PurePath`][] or [`str`][] to a valid URL, the
                resource at the given URL will be streamed to Discord when
                sending the message. Subclasses of
                [`hikari.files.WebResource`][] such as
                [`hikari.files.URL`][],
                [`hikari.messages.Attachment`][],
                [`hikari.emojis.Emoji`][],
                [`hikari.embeds.EmbedResource`][], etc will also be uploaded this way.
                This will use bit-inception, so only a small percentage of the
                resource will remain in memory at any one time, thus aiding in
                scalability.
            - If a [`hikari.files.Bytes`][] is passed, or a [`str`][]
                that contains a valid data URI is passed, then this is uploaded
                with a randomized file name if not provided.
            - If a [`hikari.files.File`][], [`pathlib.PurePath`][] or
                [`str`][] that is an absolute or relative path to a file
                on your file system is passed, then this resource is uploaded
                as an attachment using non-blocking code internally and streamed
                using bit-inception where possible. This depends on the
                type of [`concurrent.futures.Executor`][] that is being used for
                the application (default is a thread pool which supports this
                behaviour).
        attachments
            If provided, the message attachments. These can be resources, or
            strings consisting of paths on your computer or URLs.
        component
            If provided, builder object of the component to include in this message.
        components
            If provided, a sequence of the component builder objects to include
            in this message.
        embed
            If provided, the message embed.
        embeds
            If provided, the message embeds.
        poll
            If provided, the poll to create.
        sticker
            If provided, the object or ID of a sticker to send on the message.

            As of writing, bots can only send custom stickers from the current guild.
        stickers
            If provided, a sequence of the objects and IDs of up to 3 stickers
            to send on the message.

            As of writing, bots can only send custom stickers from the current guild.
        tts
            If provided, whether the message will be read out by a screen
            reader using Discord's TTS (text-to-speech) system.
        reply
            If provided, the message to reply to.
        reply_must_exist
            If provided, whether to error if the message being replied to does
            not exist instead of sending as a normal (non-reply) message.

            This will not do anything if not being used with `reply`.
        mentions_everyone
            If provided, whether the message should parse @everyone/@here
            mentions.
        mentions_reply
            If provided, whether to mention the author of the message
            that is being replied to.

            This will not do anything if not being used with `reply`.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If provided, and [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If provided, and [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.
        flags
            If provided, optional flags to set on the message. If
            [`hikari.undefined.UNDEFINED`][], then nothing is changed.

            Note that some flags may not be able to be set. Currently the only
            flags that can be set are [hikari.messages.MessageFlag.SUPPRESS_NOTIFICATIONS] and
            [hikari.messages.MessageFlag.SUPPRESS_EMBEDS].

        Returns
        -------
        hikari.messages.Message
            The created message.

        Raises
        ------
        ValueError
            If more than 100 unique objects/entities are passed for
            `role_mentions` or `user_mentions` or if both `attachment` and
            `attachments`, `component` and `components` or `embed` and `embeds`
            are specified.
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; if `reply` is not found or not in the
            same channel as `channel`; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [hikari.permissions.Permissions.SEND_MESSAGES]
            in the channel or the person you are trying to message has the DM's
            disabled.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_voice_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        attachment: files.Resourceish,
        waveform: str,
        duration: float,
        *,
        reply: undefined.UndefinedOr[snowflakes.SnowflakeishOr[messages_.PartialMessage]] = undefined.UNDEFINED,
        reply_must_exist: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_reply: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        flags: undefined.UndefinedType | int | messages_.MessageFlag = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Create a voice message in the given channel.

        Parameters
        ----------
        channel
            The channel to create the message in.
        attachment
            The audio attachment used as source for the voice message.
            This can be a resource, or string of a path on your computer
            or a URL. The Content-Type of the attachment has to start with
            `audio/`.

            Attachments can be passed as many different things, to aid in
            convenience.

            - If a [`pathlib.PurePath`][] or [`str`][] to a valid URL, the
                resource at the given URL will be streamed to Discord when
                sending the message. Subclasses of
                [`hikari.files.WebResource`][] such as
                [`hikari.files.URL`][],
                [`hikari.messages.Attachment`][], etc will also be uploaded this way.
                This will use bit-inception, so only a small percentage of the
                resource will remain in memory at any one time, thus aiding in
                scalability.
            - If a [`hikari.files.Bytes`][] is passed, or a [`str`][]
                that contains a valid data URI is passed, then this is uploaded
                with a randomized file name if not provided.
            - If a [`hikari.files.File`][], [`pathlib.PurePath`][] or
                [`str`][] that is an absolute or relative path to a file
                on your file system is passed, then this resource is uploaded
                as an attachment using non-blocking code internally and streamed
                using bit-inception where possible. This depends on the
                type of [`concurrent.futures.Executor`][] that is being used for
                the application (default is a thread pool which supports this
                behaviour).
        waveform
            The waveform of the entire voice message, with 1 byte
            per datapoint encoded in base64.

            Official clients sample the recording at most once per 100
            milliseconds, but will downsample so that no more than 256
            datapoints are in the waveform.

            !!! note
                Discord states that this is implementation detail and might
                change without notice. You have been warned!
        duration
            The duration of the voice message in seconds. This is intended to be
            a float.
        reply
            If provided, the message to reply to.
        reply_must_exist
            If provided, whether to error if the message being replied to does
            not exist instead of sending as a normal (non-reply) message.

            This will not do anything if not being used with `reply`.
        mentions_reply
            If provided, whether to mention the author of the message
            that is being replied to.

            This will not do anything if not being used with `reply`.
        flags
            If provided, optional flags to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the flags will be set
            to [`hikari.MessageFlag.IS_VOICE_MESSAGE`][], which is
            needed for sending voice messages.


            Note that some flags may not be able to be set. Currently the only
            flags that can be set are [hikari.messages.MessageFlag.SUPPRESS_NOTIFICATIONS].

        Returns
        -------
        hikari.messages.Message
            The created voice message.

        Raises
        ------
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; if `reply` is not found or not in the
            same channel as `channel`; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [hikari.permissions.Permissions.SEND_MESSAGES]
            in the channel or the person you are trying to message has the DM's
            disabled.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def crosspost_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildNewsChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
    ) -> messages_.Message:
        """Broadcast an announcement message.

        Parameters
        ----------
        channel
            The object or ID of the news channel to crosspost a message in.
        message
            The object or ID of the message to crosspost.

        Returns
        -------
        hikari.messages.Message
            The message object that was crossposted.

        Raises
        ------
        hikari.errors.BadRequestError
            If you tried to crosspost a message that has already been broadcast.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you try to crosspost a message by the current user without the
            [`hikari.permissions.Permissions.SEND_MESSAGES`][] permission for the
            target news channel or try to crosspost a message by another user
            without both the [`hikari.permissions.Permissions.SEND_MESSAGES`][]
            and [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] permissions
            for the target channel.
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def forward_message(
        self,
        channel_to: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        channel_from: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.TextableChannel]] = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Forward a message.

        Parameters
        ----------
        channel_to
            The object or ID of the channel to forward the message to.
        message
            The object or ID of the message to forward.
        channel_from
            The object or ID of the message's channel of origin.
            This field will be ignored if the message provided
              is of type [`hikari.messages.PartialMessage`][] rather than [`hikari.snowflakes.Snowflakeish`][].

        Returns
        -------
        hikari.messages.Message
            The message object that was forwarded.

        Raises
        ------
        ValueError
            If the message is of type [`hikari.snowflakes.Snowflakeish`][] and `channel_from` was not provided.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you tried to forward a message without the [`hikari.permissions.Permissions.VIEW_CHANNEL`][]
              or [`hikari.permissions.Permissions.SEND_MESSAGES`][] permissions.
        hikari.errors.NotFoundError
            If the channel or message was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discords side while handling the request.
        """

    @abc.abstractmethod
    async def edit_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        content: undefined.UndefinedOr[typing.Any] = undefined.UNDEFINED,
        *,
        attachment: undefined.UndefinedNoneOr[files.Resourceish | messages_.Attachment] = undefined.UNDEFINED,
        attachments: undefined.UndefinedNoneOr[
            typing.Sequence[files.Resourceish | messages_.Attachment]
        ] = undefined.UNDEFINED,
        component: undefined.UndefinedNoneOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedNoneOr[
            typing.Sequence[special_endpoints.ComponentBuilder]
        ] = undefined.UNDEFINED,
        embed: undefined.UndefinedNoneOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedNoneOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_reply: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
        flags: undefined.UndefinedOr[messages_.MessageFlag] = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Edit an existing message in a given channel.

        !!! warning
            If the message was not sent by your user, the only parameter
            you may provide to this call is the `flags` parameter. Anything
            else will result in a [`hikari.errors.ForbiddenError`][] being raised.

        !!! note
            Mentioning everyone, roles, or users in message edits currently
            will not send a push notification showing a new mention to people
            on Discord. It will still highlight in their chat as if they
            were mentioned, however.

            Also important to note that if you specify a text `content`, `mentions_everyone`,
            `mentions_reply`, `user_mentions`, and `role_mentions` will default
            to [`False`][] as the message will be re-parsed for mentions. This will
            also occur if only one of the four are specified

            This is a limitation of Discord's design. If in doubt, specify all
            four of them each time.

        Parameters
        ----------
        channel
            The channel to create the message in. This may be
            the object or the ID of an existing channel.
        message
            The message to edit. This may be the object or the ID
            of an existing message.
        content
            If provided, the message content to update with. If
            [`hikari.undefined.UNDEFINED`][], then the content will not
            be changed. If [`None`][], then the content will be removed.

            Any other value will be cast to a [`str`][] before sending.

            If this is a [`hikari.embeds.Embed`][] and neither the `embed` or
            `embeds` kwargs are provided or if this is a
            [`hikari.files.Resourceish`][] and neither the
            `attachment` or `attachments` kwargs are provided, the values will
            be overwritten. This allows for simpler syntax when sending an
            embed or an attachment alone.
        attachment
            If provided, the attachment to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous attachment, if
            present, is not changed. If this is [`None`][], then the
            attachment is removed, if present. Otherwise, the new attachment
            that was provided will be attached.
        attachments
            If provided, the attachments to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous attachments, if
            present, are not changed. If this is [`None`][], then the
            attachments is removed, if present. Otherwise, the new attachments
            that were provided will be attached.
        component
            If provided, builder object of the component to set for this message.
            This component will replace any previously set components and passing
            [`None`][] will remove all components.
        components
            If provided, a sequence of the component builder objects set for
            this message. These components will replace any previously set
            components and passing [`None`][] or an empty sequence will
            remove all components.
        embed
            If provided, the embed to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous embed(s) are not changed.
            If this is [`None`][] then any present embeds are removed.
            Otherwise, the new embed that was provided will be used as the
            replacement.
        embeds
            If provided, the embeds to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous embed(s) are not changed.
            If this is [`None`][] then any present embeds are removed.
            Otherwise, the new embeds that were provided will be used as the
            replacement.
        mentions_everyone
            If provided, whether the message should parse @everyone/@here
            mentions.
        mentions_reply
            If provided, whether to mention the author of the message
            that is being replied to.

            This will not do anything if not being used with `reply`.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If not provided or [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If not provided or [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.
        flags
            If provided, optional flags to set on the message. If
            [`hikari.undefined.UNDEFINED`][], then nothing is changed.

            Note that some flags may not be able to be set. Currently the only
            flags that can be set are [`hikari.messages.MessageFlag.NONE`][] and
            [`hikari.messages.MessageFlag.SUPPRESS_EMBEDS`][]. If you
            have [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] permissions, you
            can use this call to suppress embeds on another user's message.

        Returns
        -------
        hikari.messages.Message
            The edited message.

        Raises
        ------
        ValueError
            If both `attachment` and `attachments`, `component` and `components`
            or `embed` and `embeds` are specified.
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no embeds; messages with more than 2000 characters
            in them, embeds that exceed one of the many embed
            limits; invalid image URLs in embeds.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.SEND_MESSAGES`][] in the channel; if you try to
            change the contents of another user's message; or if you try to edit
            the flags on another user's message without the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][]
            permission.
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_message(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete a given message in a given channel.

        Parameters
        ----------
        channel
            The channel to delete the message in. This may be
            the object or the ID of an existing channel.
        message
            The message to delete. This may be the object or the ID of
            an existing message.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][], and the message is
            not sent by you.
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_messages(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        messages: snowflakes.SnowflakeishOr[messages_.PartialMessage]
        | typing.Iterable[snowflakes.SnowflakeishOr[messages_.PartialMessage]]
        | typing.AsyncIterable[snowflakes.SnowflakeishOr[messages_.PartialMessage]],
        /,
        *other_messages: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Bulk-delete messages from the channel.

        !!! note
            This API endpoint will only be able to delete 100 messages
            at a time. For anything more than this, multiple requests will
            be executed one-after-the-other, since the rate limits for this
            endpoint do not favour more than one request per bucket.

            If one message is left over from chunking per 100 messages, or
            only one message is passed to this coroutine function, then the
            logic is expected to defer to `delete_message`. The implication
            of this is that the `delete_message` endpoint is rate limited
            by a different bucket with different usage rates.

        !!! warning
            This endpoint is not atomic. If an error occurs midway through
            a bulk delete, you will **not** be able to revert any changes made
            up to this point.

        !!! warning
            Specifying any messages more than 14 days old will cause the call
            to fail, potentially with partial completion.

        Parameters
        ----------
        channel
            The channel to bulk delete the messages in. This may be
            the object or the ID of an existing channel.
        messages
            Either the object/ID of an existing message to delete or an iterable
            (sync or async) of the objects and/or IDs of existing messages to delete.
        *other_messages
            The objects and/or IDs of other existing messages to delete.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.BulkDeleteError
            An error containing the messages successfully deleted, and the
            messages that were not removed. The
            [`BaseException.__cause__`][] of the exception will be the
            original error that terminated this process.
        """

    @abc.abstractmethod
    async def add_reaction(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        emoji: str | emojis.Emoji,
        emoji_id: undefined.UndefinedOr[snowflakes.SnowflakeishOr[emojis.CustomEmoji]] = undefined.UNDEFINED,
    ) -> None:
        """Add a reaction emoji to a message in a given channel.

        Parameters
        ----------
        channel
            The channel where the message to add the reaction to is. This
            may be a [`hikari.channels.TextableChannel`][] or the ID of an existing
            channel.
        message
            The message to add a reaction to. This may be the
            object or the ID of an existing message.
        emoji
            Object or name of the emoji to react with.
        emoji_id
            ID of the custom emoji to react with.
            This should only be provided when a custom emoji's name is passed
            for `emoji`.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid unicode emoji is given, or if the given custom emoji
            does not exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.ADD_REACTIONS`][] (this is only necessary if you
            are the first person to add the reaction).
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_my_reaction(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        emoji: str | emojis.Emoji,
        emoji_id: undefined.UndefinedOr[snowflakes.SnowflakeishOr[emojis.CustomEmoji]] = undefined.UNDEFINED,
    ) -> None:
        """Delete a reaction that your application user created.

        Parameters
        ----------
        channel
            The channel where the message to delete the reaction from is.
            This may be the object or the ID of an existing channel.
        message
            The message to delete a reaction from. This may be the
            object or the ID of an existing message.
        emoji
            Object or name of the emoji to remove your reaction for.
        emoji_id
            ID of the custom emoji to remove your reaction for.
            This should only be provided when a custom emoji's name is passed
            for `emoji`.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid unicode emoji is given, or if the given custom emoji
            does not exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_all_reactions_for_emoji(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        emoji: str | emojis.Emoji,
        emoji_id: undefined.UndefinedOr[snowflakes.SnowflakeishOr[emojis.CustomEmoji]] = undefined.UNDEFINED,
    ) -> None:
        """Delete all reactions for a single emoji on a given message.

        Parameters
        ----------
        channel
            The channel where the message to delete the reactions from is.
            This may be the object or the ID of an existing channel.
        message
            The message to delete a reactions from. This may be the
            object or the ID of an existing message.
        emoji
            Object or name of the emoji to remove all the reactions for.
        emoji_id
            ID of the custom emoji to remove all the reactions for.
            This should only be provided when a custom emoji's name is passed
            for `emoji`.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid unicode emoji is given, or if the given custom emoji
            does not exist.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_reaction(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        emoji: str | emojis.Emoji,
        emoji_id: undefined.UndefinedOr[snowflakes.SnowflakeishOr[emojis.CustomEmoji]] = undefined.UNDEFINED,
    ) -> None:
        """Delete a reaction from a message.

        If you are looking to delete your own applications reaction, use
        `delete_my_reaction`.

        Parameters
        ----------
        channel
            The channel where the message to delete the reaction from is.
            This may be the object or the ID of an existing channel.
        message
            The message to delete a reaction from. This may be the
            object or the ID of an existing message.
        user
            Object or ID of the user to remove the reaction of.
        emoji
            Object or name of the emoji to react with.
        emoji_id
            ID of the custom emoji to react with.
            This should only be provided when a custom emoji's name is passed
            for `emoji`.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid unicode emoji is given, or if the given custom emoji
            does not exist.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_all_reactions(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
    ) -> None:
        """Delete all reactions from a message.

        Parameters
        ----------
        channel
            The channel where the message to delete all reactions from is.
            This may be the object or the ID of an existing channel.
        message
            The message to delete all reaction from. This may be the
            object or the ID of an existing message.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid unicode emoji is given, or if the given custom emoji
            does not exist.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_MESSAGES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_reactions_for_emoji(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        emoji: str | emojis.Emoji,
        emoji_id: undefined.UndefinedOr[snowflakes.SnowflakeishOr[emojis.CustomEmoji]] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[users.User]:
        """Fetch reactions for an emoji from a message.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it,
            thus any errors documented below will happen then.

            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        channel
            The channel where the message to delete all reactions from is.
            This may be the object or the ID of an existing channel.
        message
            The message to delete all reaction from. This may be the
            object or the ID of an existing message.
        emoji
            Object or name of the emoji to get the reactions for.
        emoji_id
            ID of the custom emoji to get the reactions for.
            This should only be provided when a custom emoji's name is passed
            for `emoji`.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.users.User]
            An iterator to fetch the users.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid unicode emoji is given, or if the given custom emoji
            does not exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel or message is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_webhook(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.WebhookChannelT],
        name: str,
        *,
        avatar: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> webhooks.IncomingWebhook:
        """Create webhook in a channel.

        Parameters
        ----------
        channel
            The channel where the webhook will be created. This may be
            the object or the ID of an existing channel.
        name
            The name for the webhook. This cannot be `clyde`.
        avatar
            If provided, the avatar for the webhook.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.webhooks.IncomingWebhook
            The created webhook.

        Raises
        ------
        hikari.errors.BadRequestError
            If `name` doesn't follow the restrictions enforced by discord.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_webhook(
        self,
        webhook: snowflakes.SnowflakeishOr[webhooks.PartialWebhook],
        *,
        token: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> webhooks.PartialWebhook:
        """Fetch an existing webhook.

        Parameters
        ----------
        webhook
            The webhook to fetch. This may be the object or the ID
            of an existing webhook.
        token
            If provided, the webhook token that will be used to fetch
            the webhook instead of the token the client was initialized with.

        Returns
        -------
        hikari.webhooks.PartialWebhook
            The requested webhook.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission when not
            using a token.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_channel_webhooks(
        self, channel: snowflakes.SnowflakeishOr[channels_.WebhookChannelT]
    ) -> typing.Sequence[webhooks.PartialWebhook]:
        """Fetch all channel webhooks.

        Parameters
        ----------
        channel
            The channel to fetch the webhooks for. This may be an instance of any
            of the classes which are valid for [`hikari.channels.WebhookChannelT`][]
            or the ID of an existing channel.

        Returns
        -------
        typing.Sequence[hikari.webhooks.PartialWebhook]
            The fetched webhooks.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_webhooks(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[webhooks.PartialWebhook]:
        """Fetch all guild webhooks.

        Parameters
        ----------
        guild
            The guild to fetch the webhooks for. This may be the object
            or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.webhooks.PartialWebhook]
            The fetched webhooks.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_webhook(
        self,
        webhook: snowflakes.SnowflakeishOr[webhooks.PartialWebhook],
        *,
        token: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        avatar: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        channel: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.WebhookChannelT]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> webhooks.PartialWebhook:
        """Edit a webhook.

        Parameters
        ----------
        webhook
            The webhook to edit. This may be the object or the
            ID of an existing webhook.
        token
            If provided, the webhook token that will be used to edit
            the webhook instead of the token the client was initialized with.
        name
            If provided, the new webhook name.
        avatar
            If provided, the new webhook avatar. If [`None`][], will
            remove the webhook avatar.
        channel
            If provided, the text channel to move the webhook to.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.webhooks.PartialWebhook
            The edited webhook.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission when not
            using a token.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_webhook(
        self,
        webhook: snowflakes.SnowflakeishOr[webhooks.PartialWebhook],
        *,
        token: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete a webhook.

        Parameters
        ----------
        webhook
            The webhook to delete. This may be the object or the
            ID of an existing webhook.
        token
            If provided, the webhook token that will be used to delete
            the webhook instead of the token the client was initialized with.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_WEBHOOKS`][] permission when not
            using a token.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def execute_webhook_voice_message(
        self,
        # MyPy might not say this but SnowflakeishOr[ExecutableWebhook] isn't valid as ExecutableWebhook isn't Unique
        webhook: webhooks.ExecutableWebhook | snowflakes.Snowflakeish,
        token: str,
        attachment: files.Resourceish,
        waveform: str,
        duration: float,
        *,
        thread: undefined.UndefinedType | snowflakes.SnowflakeishOr[channels_.GuildThreadChannel] = undefined.UNDEFINED,
        username: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        avatar_url: undefined.UndefinedType | str | files.URL = undefined.UNDEFINED,
        flags: undefined.UndefinedType | int | messages_.MessageFlag = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Execute a webhook, by sending a voice message.

        !!! warning
            At the time of writing, `username` and `avatar_url` are ignored for
            interaction webhooks.

            Additionally, [`hikari.messages.MessageFlag.SUPPRESS_EMBEDS`][],
            [`hikari.messages.MessageFlag.SUPPRESS_NOTIFICATIONS`][] and
            [`hikari.messages.MessageFlag.EPHEMERAL`][] are the only flags that
            can be set, with [`hikari.messages.MessageFlag.EPHEMERAL`][] limited to
            interaction webhooks.

        Parameters
        ----------
        webhook
            The webhook to execute. This may be the object
            or the ID of an existing webhook.
        token
            The webhook token.
        attachment
            The audio attachment used as source for the voice message.
            This can be a resource, or string of a path on your computer
            or a URL. The Content-Type of the attachment has to start with
            `audio/`.


            Attachments can be passed as many different things, to aid in
            convenience.

            - If a [`pathlib.PurePath`][] or [`str`][] to a valid URL, the
                resource at the given URL will be streamed to Discord when
                sending the message. Subclasses of
                [`hikari.files.WebResource`][] such as
                [`hikari.files.URL`][],
                [`hikari.messages.Attachment`][],
                [`hikari.emojis.Emoji`][],
                [`hikari.embeds.EmbedResource`][], etc. will also be uploaded this way.
                This will use bit-inception, so only a small percentage of the
                resource will remain in memory at any one time, thus aiding in
                scalability.
            - If a [hikari.files.Bytes] is passed, or a [`str`][]
                that contains a valid data URI is passed, then this is uploaded
                with a randomized file name if not provided.
            - If a [hikari.files.File], [`pathlib.PurePath`][] or
                [`str`][] that is an absolute or relative path to a file
                on your file system is passed, then this resource is uploaded
                as an attachment using non-blocking code internally and streamed
                using bit-inception where possible. This depends on the
                type of [`concurrent.futures.Executor`][] that is being used for
                the application (default is a thread pool which supports this
                behaviour).
        waveform
            The waveform of the entire voice message, with 1 byte
            per datapoint encoded in base64.

            Official clients sample the recording at most once per 100
            milliseconds, but will downsample so that no more than 256
            datapoints are in the waveform.

            !!! note
                Discord states that this is implementation detail and might
                change without notice. You have been warned!
        duration
            The duration of the voice message in seconds. This is intended to be
            a float.
        thread
            If provided then the message will be created in the target thread
            within the webhook's channel, otherwise it will be created in
            the webhook's target channel.

            This is required when trying to create a thread message.
        username
            If provided, the username to override the webhook's username
            for this request.
        avatar_url
            If provided, the url of an image to override the webhook's
            avatar with for this request.
        flags
            The flags to set for this webhook message.

        Returns
        -------
        hikari.messages.Message
            The created message.

        Raises
        ------
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def execute_webhook(
        self,
        # MyPy might not say this but SnowflakeishOr[ExecutableWebhook] isn't valid as ExecutableWebhook isn't Unique
        webhook: webhooks.ExecutableWebhook | snowflakes.Snowflakeish,
        token: str,
        content: undefined.UndefinedOr[typing.Any] = undefined.UNDEFINED,
        *,
        thread: undefined.UndefinedType | snowflakes.SnowflakeishOr[channels_.GuildThreadChannel] = undefined.UNDEFINED,
        username: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        avatar_url: undefined.UndefinedType | str | files.URL = undefined.UNDEFINED,
        attachment: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        attachments: undefined.UndefinedOr[typing.Sequence[files.Resourceish]] = undefined.UNDEFINED,
        component: undefined.UndefinedOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedOr[typing.Sequence[special_endpoints.ComponentBuilder]] = undefined.UNDEFINED,
        embed: undefined.UndefinedOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        poll: undefined.UndefinedOr[special_endpoints.PollBuilder] = undefined.UNDEFINED,
        tts: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
        flags: undefined.UndefinedType | int | messages_.MessageFlag = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Execute a webhook.

        !!! warning
            At the time of writing, `username` and `avatar_url` are ignored for
            interaction webhooks.

            Additionally, [`hikari.messages.MessageFlag.SUPPRESS_EMBEDS`][],
            [`hikari.messages.MessageFlag.SUPPRESS_NOTIFICATIONS`][] and
            [`hikari.messages.MessageFlag.EPHEMERAL`][] are the only flags that
            can be set, with [`hikari.messages.MessageFlag.EPHEMERAL`][] limited to
            interaction webhooks.

        Parameters
        ----------
        webhook
            The webhook to execute. This may be the object
            or the ID of an existing webhook.
        token
            The webhook token.
        content
            If provided, the message contents. If
            [`hikari.undefined.UNDEFINED`][], then nothing will be sent
            in the content. Any other value here will be cast to a
            [`str`][].

            If this is a [`hikari.embeds.Embed`][] and no `embed` nor
            no `embeds` kwarg is provided, then this will instead
            update the embed. This allows for simpler syntax when
            sending an embed alone.

            Likewise, if this is a [`hikari.files.Resource`][], then the
            content is instead treated as an attachment if no `attachment` and
            no `attachments` kwargs are provided.
        thread
            If provided then the message will be created in the target thread
            within the webhook's channel, otherwise it will be created in
            the webhook's target channel.

            This is required when trying to create a thread message.
        username
            If provided, the username to override the webhook's username
            for this request.
        avatar_url
            If provided, the url of an image to override the webhook's
            avatar with for this request.
        attachment
            If provided, the message attachment. This can be a resource,
            or string of a path on your computer or a URL.

            Attachments can be passed as many different things, to aid in
            convenience.

            - If a [`pathlib.PurePath`][] or [`str`][] to a valid URL, the
                resource at the given URL will be streamed to Discord when
                sending the message. Subclasses of
                [`hikari.files.WebResource`][] such as
                [`hikari.files.URL`][],
                [`hikari.messages.Attachment`][],
                [`hikari.emojis.Emoji`][],
                [`hikari.embeds.EmbedResource`][], etc. will also be uploaded this way.
                This will use bit-inception, so only a small percentage of the
                resource will remain in memory at any one time, thus aiding in
                scalability.
            - If a [hikari.files.Bytes] is passed, or a [`str`][]
                that contains a valid data URI is passed, then this is uploaded
                with a randomized file name if not provided.
            - If a [hikari.files.File], [`pathlib.PurePath`][] or
                [`str`][] that is an absolute or relative path to a file
                on your file system is passed, then this resource is uploaded
                as an attachment using non-blocking code internally and streamed
                using bit-inception where possible. This depends on the
                type of [`concurrent.futures.Executor`][] that is being used for
                the application (default is a thread pool which supports this
                behaviour).
        attachments
            If provided, the message attachments. These can be resources, or
            strings consisting of paths on your computer or URLs.
        component
            If provided, builder object of the component to include in this message.
        components
            If provided, a sequence of the component builder objects to include
            in this message.
        embed
            If provided, the message embed.
        embeds
            If provided, the message embeds.
        poll
            If provided, the message poll.
        tts
            If provided, whether the message will be read out by a screen
            reader using Discord's TTS (text-to-speech) system.
        mentions_everyone
            If provided, whether the message should parse @everyone/@here
            mentions.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If provided, and [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If provided, and [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.
        flags
            The flags to set for this webhook message.

        Returns
        -------
        hikari.messages.Message
            The created message.

        Raises
        ------
        ValueError
            If more than 100 unique objects/entities are passed for
            `role_mentions` or `user_mentions` or if both `attachment` and
            `attachments` or `embed` and `embeds` are specified.
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_webhook_message(
        self,
        # MyPy might not say this but SnowflakeishOr[ExecutableWebhook] isn't valid as ExecutableWebhook isn't Unique
        webhook: webhooks.ExecutableWebhook | snowflakes.Snowflakeish,
        token: str,
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        *,
        thread: undefined.UndefinedType | snowflakes.SnowflakeishOr[channels_.GuildThreadChannel] = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Fetch an old message sent by the webhook.

        Parameters
        ----------
        webhook
            The webhook to execute. This may be the object
            or the ID of an existing webhook.
        token
            The webhook token.
        message
            The message to fetch. This may be the object or the ID of an
            existing channel.
        thread
            If provided then the message will be fetched from the target thread
            within the webhook's channel, otherwise it will be fetched from
            the webhook's target channel.

            This is required when trying to fetch a thread message.

        Returns
        -------
        hikari.messages.Message
            The requested message.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook is not found or the webhook's message wasn't found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_webhook_message(
        self,
        # MyPy might not say this but SnowflakeishOr[ExecutableWebhook] isn't valid as ExecutableWebhook isn't Unique
        webhook: webhooks.ExecutableWebhook | snowflakes.Snowflakeish,
        token: str,
        message: snowflakes.SnowflakeishOr[messages_.Message],
        content: undefined.UndefinedNoneOr[typing.Any] = undefined.UNDEFINED,
        *,
        thread: undefined.UndefinedType | snowflakes.SnowflakeishOr[channels_.GuildThreadChannel] = undefined.UNDEFINED,
        attachment: undefined.UndefinedNoneOr[files.Resourceish | messages_.Attachment] = undefined.UNDEFINED,
        attachments: undefined.UndefinedNoneOr[
            typing.Sequence[files.Resourceish | messages_.Attachment]
        ] = undefined.UNDEFINED,
        component: undefined.UndefinedNoneOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedNoneOr[
            typing.Sequence[special_endpoints.ComponentBuilder]
        ] = undefined.UNDEFINED,
        embed: undefined.UndefinedNoneOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedNoneOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Edit a message sent by a webhook.

         !!! note
            Mentioning everyone, roles, or users in message edits currently
            will not send a push notification showing a new mention to people
            on Discord. It will still highlight in their chat as if they
            were mentioned, however.

            Also important to note that if you specify a text `content`, `mentions_everyone`,
            `mentions_reply`, `user_mentions`, and `role_mentions` will default
            to [`False`][] as the message will be re-parsed for mentions. This will
            also occur if only one of the four are specified

            This is a limitation of Discord's design. If in doubt, specify all
            four of them each time.

        Parameters
        ----------
        webhook
            The webhook to execute. This may be the object
            or the ID of an existing webhook.
        token
            The webhook token.
        message
            The message to delete. This may be the object or the ID of
            an existing message.
        content
            If provided, the message content to update with. If
            [`hikari.undefined.UNDEFINED`][], then the content will not
            be changed. If [`None`][], then the content will be removed.

            Any other value will be cast to a [`str`][] before sending.

            If this is a [`hikari.embeds.Embed`][] and neither the
            `embed` or `embeds` kwargs are provided or if this is a
            [`hikari.files.Resourceish`][] and neither the `attachment` or
            `attachments` kwargs are provided, the values will be overwritten.
            This allows for simpler syntax when sending an embed or an
            attachment alone.
        thread
            If provided then the message will be edited in the target thread
            within the webhook's channel, otherwise it will be edited in
            the webhook's target channel.

            This is required when trying to edit a thread message.
        attachment
            If provided, the attachment to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous attachment, if
            present, is not changed. If this is [`None`][], then the
            attachment is removed, if present. Otherwise, the new attachment
            that was provided will be attached.
        attachments
            If provided, the attachments to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous attachments, if
            present, are not changed. If this is [`None`][], then the
            attachments is removed, if present. Otherwise, the new attachments
            that were provided will be attached.
        component
            If provided, builder object of the component to set for this message.
            This component will replace any previously set components and passing
            [`None`][] will remove all components.
        components
            If provided, a sequence of the component builder objects set for
            this message. These components will replace any previously set
            components and passing [`None`][] or an empty sequence will
            remove all components.
        embed
            If provided, the embed to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous embed(s) are not changed.
            If this is [`None`][] then any present embeds are removed.
            Otherwise, the new embed that was provided will be used as the
            replacement.
        embeds
            If provided, the embeds to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous embed(s) are not changed.
            If this is [`None`][] then any present embeds are removed.
            Otherwise, the new embeds that were provided will be used as the
            replacement.
        mentions_everyone
            If provided, sanitation for `@everyone` mentions. If
            [`hikari.undefined.UNDEFINED`][], then the previous setting is
            not changed. If [`True`][], then `@everyone`/`@here` mentions
            in the message content will show up as mentioning everyone that can
            view the chat.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If provided, and [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If provided, and [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.

        Returns
        -------
        hikari.messages.Message
            The edited message.

        Raises
        ------
        ValueError
            If both `attachment` and `attachments`, `component` and `components`
            or `embed` and `embeds` are specified.
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook or the message are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_webhook_message(
        self,
        # MyPy might not say this but SnowflakeishOr[ExecutableWebhook] isn't valid as ExecutableWebhook isn't Unique
        webhook: webhooks.ExecutableWebhook | snowflakes.Snowflakeish,
        token: str,
        message: snowflakes.SnowflakeishOr[messages_.Message],
        *,
        thread: undefined.UndefinedType | snowflakes.SnowflakeishOr[channels_.GuildThreadChannel] = undefined.UNDEFINED,
    ) -> None:
        """Delete a given message in a given channel.

        Parameters
        ----------
        webhook
            The webhook to execute. This may be the object
            or the ID of an existing webhook.
        token
            The webhook token.
        message
            The message to delete. This may be the object or the ID of
            an existing message.
        thread
            If provided then the message will be deleted from the target thread
            within the webhook's channel, otherwise it will be deleted from
            the webhook's target channel.

            This is required when trying to delete a thread message.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the webhook or the message are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_gateway_url(self) -> str:
        """Fetch the gateway url.

        !!! note
            This endpoint does not require any valid authorization.

        Raises
        ------
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_gateway_bot_info(self) -> sessions.GatewayBotInfo:
        """Fetch the gateway info for the bot.

        Returns
        -------
        hikari.sessions.GatewayBotInfo
            The gateway bot information.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_invite(self, invite: invites.InviteCode | str, *, with_counts: bool = True) -> invites.Invite:
        """Fetch an existing invite.

        Parameters
        ----------
        invite
            The invite to fetch. This may be an invite object or
            the code of an existing invite.
        with_counts
            Whether the invite should contain the approximate member counts.

        Returns
        -------
        hikari.invites.Invite
            The requested invite.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the invite is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_invite(
        self, invite: invites.InviteCode | str, reason: undefined.UndefinedOr[str] = undefined.UNDEFINED
    ) -> invites.Invite:
        """Delete an existing invite.

        Parameters
        ----------
        invite
            The invite to delete. This may be an invite object or
            the code of an existing invite.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.invites.Invite
            Object of the invite that was deleted.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission in the guild
            the invite is from or if you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][]
            permission in the channel the invite is from.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the invite is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_my_user(self) -> users.OwnUser:
        """Fetch the token's associated user.

        Returns
        -------
        hikari.users.OwnUser
            The token's associated user.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_my_user(
        self,
        *,
        username: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        avatar: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        banner: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
    ) -> users.OwnUser:
        """Edit the token's associated user.

        Parameters
        ----------
        username
            If provided, the new username.
        avatar
            If provided, the new avatar. If [`None`][],
            the avatar will be removed.
        banner
            If provided, the new banner. If [`None`][],
            the banner will be removed.

        Returns
        -------
        hikari.users.OwnUser
            The edited token's associated user.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.

            Discord also returns this on a rate limit:
            <https://github.com/discord/discord-api-docs/issues/1462>
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_my_connections(self) -> typing.Sequence[applications.OwnConnection]:
        """Fetch the token's associated connections.

        Returns
        -------
        hikari.applications.OwnConnection
            The token's associated connections.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_my_guilds(
        self,
        *,
        newest_first: bool = False,
        start_at: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[applications.OwnGuild]:
        """Fetch the token's associated guilds.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it,
            thus any errors documented below will happen then.

            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        newest_first
            Whether to fetch the newest first or the oldest first.
        start_at
            If provided, will start at this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may also be a guild object. In this case, the
            date the object was first created will be used.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.applications.OwnGuild]
            The token's associated guilds.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def leave_guild(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], /) -> None:
        """Leave a guild.

        Parameters
        ----------
        guild
            The guild to leave. This may be the object or
            the ID of an existing guild.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found or you own the guild.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_my_user_application_role_connection(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication]
    ) -> applications.OwnApplicationRoleConnection:
        """Fetch the token's associated role connections.

        !!! note
            This requires the token to have the
            [`hikari.applications.OAuth2Scope.ROLE_CONNECTIONS_WRITE`][] scope enabled.

        Parameters
        ----------
        application
            The application to fetch the application role connections for.

        Returns
        -------
        hikari.applications.OwnApplicationRoleConnection
            The requested role connection.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the application is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def set_my_user_application_role_connection(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        platform_name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        platform_username: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        metadata: undefined.UndefinedOr[
            typing.Mapping[str, str | int | bool | datetime.datetime]
        ] = undefined.UNDEFINED,
    ) -> applications.OwnApplicationRoleConnection:
        """Set the token's associated role connections.

        !!! note
            This requires the token to have the
            [`hikari.applications.OAuth2Scope.ROLE_CONNECTIONS_WRITE`][] scope enabled.

        Parameters
        ----------
        application
            The application to set the application role connections for.
        platform_name
            If provided, the name of the platform that will be connected.
        platform_username
            If provided, the name of the user in the platform.
        metadata
            If provided, the role connection metadata.

            Depending on the time of the previously created application role
            records through `set_application_role_connection_metadata_records`,
            this mapping should contain those keys to the valid type of the record:

                - `INTEGER_X`: An [`int`][].
                - `DATETIME_X`: A [`datetime.datetime`][] object.
                - `BOOLEAN_X`: A [`bool`][].

        Returns
        -------
        hikari.applications.OwnApplicationRoleConnection
            The set role connection.

        Raises
        ------
        hikari.errors.BadRequestError
            If incorrect values are provided or unknown keys are provided in the metadata.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the application is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_dm_channel(self, user: snowflakes.SnowflakeishOr[users.PartialUser], /) -> channels_.DMChannel:
        """Create a DM channel with a user.

        Parameters
        ----------
        user
            The user to create the DM channel with. This may be the
            object or the ID of an existing user.

        Returns
        -------
        hikari.channels.DMChannel
            The created DM channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If the user is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    # THIS IS AN OAUTH2 FLOW BUT CAN ALSO BE USED BY BOTS
    @abc.abstractmethod
    async def fetch_application(self) -> applications.Application:
        """Fetch the token's associated application.

        !!! warning
            This endpoint can only be used with a Bot token. Using this with a
            Bearer token will result in a [`hikari.errors.UnauthorizedError`][].

        Returns
        -------
        hikari.applications.Application
            The token's associated application.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    # THIS IS AN OAUTH2 FLOW ONLY
    @abc.abstractmethod
    async def fetch_authorization(self) -> applications.AuthorizationInformation:
        """Fetch the token's authorization information.

        !!! warning
            This endpoint can only be used with a Bearer token. Using this
            with a Bot token will result in a [`hikari.errors.UnauthorizedError`][].

        Returns
        -------
        hikari.applications.AuthorizationInformation
            The token's authorization information.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_application_role_connection_metadata_records(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication]
    ) -> typing.Sequence[applications.ApplicationRoleConnectionMetadataRecord]:
        """Fetch the application role connection metadata records.

        !!! note
            This requires the token to have the
            [`hikari.applications.OAuth2Scope.ROLE_CONNECTIONS_WRITE`][] scope enabled.

        Parameters
        ----------
        application
            The application to fetch the application role connection metadata records for.

        Returns
        -------
        typing.Sequence[hikari.applications.ApplicationRoleConnectionMetadataRecord]
            The requested application role connection metadata records.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the application is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def set_application_role_connection_metadata_records(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        records: typing.Sequence[applications.ApplicationRoleConnectionMetadataRecord],
    ) -> typing.Sequence[applications.ApplicationRoleConnectionMetadataRecord]:
        """Set the application role connection metadata records.

        !!! note
            This requires the token to have the
            [`hikari.applications.OAuth2Scope.ROLE_CONNECTIONS_WRITE`][] scope enabled.

        Parameters
        ----------
        application
            The application to set the application role connection metadata records for.
        records
            The records to set for the application.

        Returns
        -------
        typing.Sequence[hikari.applications.ApplicationRoleConnectionMetadataRecord]
            The set application role connection metadata records.

        Raises
        ------
        hikari.errors.BadRequestError
            If incorrect values are provided for the records.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the application is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def authorize_client_credentials_token(
        self,
        client: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        client_secret: str,
        # While according to the spec scopes are optional here, Discord requires that "valid" scopes are passed.
        scopes: typing.Sequence[applications.OAuth2Scope | str],
    ) -> applications.PartialOAuth2Token:
        """Authorize a client credentials token for an application.

        Parameters
        ----------
        client
            Object or ID of the application to authorize as.
        client_secret
            Secret of the application to authorize as.
        scopes
            The scopes to authorize for.

        Returns
        -------
        hikari.applications.PartialOAuth2Token
            Object of the authorized partial OAuth2 token.

        Raises
        ------
        hikari.errors.BadRequestError
            If invalid any invalid or malformed scopes are passed.
        hikari.errors.UnauthorizedError
            When an client or client secret is passed.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def authorize_access_token(
        self,
        client: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        client_secret: str,
        code: str,
        redirect_uri: str,
    ) -> applications.OAuth2AuthorizationToken:
        """Authorize an OAuth2 token using the authorize code grant type.

        Parameters
        ----------
        client
            Object or ID of the application to authorize with.
        client_secret
            Secret of the application to authorize with.
        code
            The authorization code to exchange for an OAuth2 access token.
        redirect_uri
            The redirect uri that was included in the authorization request.

        Returns
        -------
        hikari.applications.OAuth2AuthorizationToken
            Object of the authorized OAuth2 token.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid redirect uri or code is passed.
        hikari.errors.UnauthorizedError
            When an client or client secret is passed.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def refresh_access_token(
        self,
        client: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        client_secret: str,
        refresh_token: str,
        *,
        scopes: undefined.UndefinedOr[typing.Sequence[applications.OAuth2Scope | str]] = undefined.UNDEFINED,
    ) -> applications.OAuth2AuthorizationToken:
        """Refresh an access token.

        !!! warning
            As of writing this Discord currently ignores any passed scopes,
            therefore you should use
            [`hikari.applications.OAuth2AuthorizationToken.scopes`][] to validate
            that the expected scopes were actually authorized here.

        Parameters
        ----------
        client
            Object or ID of the application to authorize with.
        client_secret
            Secret of the application to authorize with.
        refresh_token
            The refresh token to use.
        scopes
            The scope of the access request.

        Returns
        -------
        hikari.applications.OAuth2AuthorizationToken
            Object of the authorized OAuth2 token.

        Raises
        ------
        hikari.errors.BadRequestError
            If an invalid redirect uri or refresh_token is passed.
        hikari.errors.UnauthorizedError
            When an client or client secret is passed.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def revoke_access_token(
        self,
        client: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        client_secret: str,
        token: str | applications.PartialOAuth2Token,
    ) -> None:
        """Revoke an OAuth2 token.

        Parameters
        ----------
        client
            Object or ID of the application to authorize with.
        client_secret
            Secret of the application to authorize with.
        token
            Object or string of the access token to revoke.

        Raises
        ------
        hikari.errors.UnauthorizedError
            When an client or client secret is passed.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    # THIS IS AN OAUTH2 FLOW ONLY
    @abc.abstractmethod
    async def add_user_to_guild(
        self,
        access_token: str | applications.PartialOAuth2Token,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        nickname: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        mute: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        deaf: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> guilds.Member | None:
        """Add a user to a guild.

        !!! note
            This requires the `access_token` to have the
            [`hikari.applications.OAuth2Scope.GUILDS_JOIN`][] scope enabled along
            with the authorization of a Bot which has [`hikari.permissions.Permissions.CREATE_INSTANT_INVITE`][]
            permission within the target guild.

        Parameters
        ----------
        access_token
            Object or string of the access token to use for this request.
        guild
            The guild to add the user to. This may be the object
            or the ID of an existing guild.
        user
            The user to add to the guild. This may be the object
            or the ID of an existing user.
        nickname
            If provided, the nick to add to the user when he joins the guild.

            Requires the [`hikari.permissions.Permissions.MANAGE_NICKNAMES`][] permission on the guild.
        roles
            If provided, the roles to add to the user when he joins the guild.
            This may be a collection objects or IDs of existing roles.

            Requires the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission on the guild.
        mute
            If provided, the mute state to add the user when he joins the guild.

            Requires the [`hikari.permissions.Permissions.MUTE_MEMBERS`][] permission on the guild.
        deaf
            If provided, the deaf state to add the user when he joins the guild.

            Requires the [`hikari.permissions.Permissions.DEAFEN_MEMBERS`][] permission on the guild.

        Returns
        -------
        typing.Optional[hikari.guilds.Member]
            [`None`][] if the user was already part of the guild, else
            [`hikari.guilds.Member`][].

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are not part of the guild you want to add the user to,
            if you are missing permissions to do one of the things you specified,
            if you are using an access token for another user, if the token is
            bound to another bot or if the access token doesn't have the
            [`hikari.applications.OAuth2Scope.GUILDS_JOIN`][] scope enabled.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If you own the guild or the user is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_voice_regions(self) -> typing.Sequence[voices.VoiceRegion]:
        """Fetch available voice regions.

        Returns
        -------
        typing.Sequence[hikari.voices.VoiceRegion]
            The available voice regions.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_user(self, user: snowflakes.SnowflakeishOr[users.PartialUser]) -> users.User:
        """Fetch a user.

        Parameters
        ----------
        user
            The user to fetch. This can be the object
            or the ID of an existing user.

        Returns
        -------
        hikari.users.User
            The requested user.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the user is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_audit_log(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        before: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[snowflakes.Unique]] = undefined.UNDEFINED,
        user: undefined.UndefinedOr[snowflakes.SnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
        event_type: undefined.UndefinedOr[audit_logs.AuditLogEventType | int] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[audit_logs.AuditLog]:
        """Fetch pages of the guild's audit log.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it,
            thus any errors documented below will happen then.

            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        guild
            The guild to fetch the audit logs from. This can be a
            guild object or the ID of an existing guild.
        before
            If provided, filter to only actions before this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may be any other Discord entity that has an ID. In this case, the
            date the object was first created will be used.
        user
            If provided, the user to filter for.
        event_type
            If provided, the event type to filter for.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.audit_logs.AuditLog]
            The guild's audit log.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.VIEW_AUDIT_LOG`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_emoji(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        emoji: snowflakes.SnowflakeishOr[emojis.CustomEmoji],
    ) -> emojis.KnownCustomEmoji:
        """Fetch a guild emoji.

        Parameters
        ----------
        guild
            The guild to fetch the emoji from. This can be a
            guild object or the ID of an existing guild.
        emoji
            The emoji to fetch. This can be a [`hikari.emojis.CustomEmoji`][]
            or the ID of an existing emoji.

        Returns
        -------
        hikari.emojis.KnownCustomEmoji
            The requested emoji.

        Raises
        ------
        hikari.errors.NotFoundError
            If the guild or the emoji are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_emojis(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[emojis.KnownCustomEmoji]:
        """Fetch the emojis of a guild.

        Parameters
        ----------
        guild
            The guild to fetch the emojis from. This can be a
            guild object or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.emojis.KnownCustomEmoji]
            The requested emojis.

        Raises
        ------
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_emoji(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        image: files.Resourceish,
        *,
        roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> emojis.KnownCustomEmoji:
        """Create an emoji in a guild.

        Parameters
        ----------
        guild
            The guild to create the emoji on. This can be a
            guild object or the ID of an existing guild.
        name
            The name for the emoji.
        image
            The 128x128 image for the emoji. Maximum upload size is 256kb.
            This can be a still or an animated image.
        roles
            If provided, a collection of the roles that will be able to
            use this emoji. This can be a [`hikari.guilds.PartialRole`][] or
            the ID of an existing role.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.emojis.KnownCustomEmoji
            The created emoji.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value or
            if there are no more spaces for the type of emoji in the guild.
        hikari.errors.ForbiddenError
            If you are missing [`hikari.permissions.Permissions.MANAGE_GUILD_EXPRESSIONS`][]
            in the server.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_emoji(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        emoji: snowflakes.SnowflakeishOr[emojis.CustomEmoji],
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> emojis.KnownCustomEmoji:
        """Edit an emoji in a guild.

        Parameters
        ----------
        guild
            The guild to edit the emoji on. This can be a
            guild object or the ID of an existing guild.
        emoji
            The emoji to edit. This can be a [`hikari.emojis.CustomEmoji`][]
            or the ID of an existing emoji.
        name
            If provided, the new name for the emoji.
        roles
            If provided, the new collection of roles that will be able to
            use this emoji. This can be a [`hikari.guilds.PartialRole`][] or
            the ID of an existing role.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.emojis.KnownCustomEmoji
            The edited emoji.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing [`hikari.permissions.Permissions.MANAGE_GUILD_EXPRESSIONS`][]
            in the server.
        hikari.errors.NotFoundError
            If the guild or the emoji are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_emoji(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        emoji: snowflakes.SnowflakeishOr[emojis.CustomEmoji],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete an emoji in a guild.

        Parameters
        ----------
        guild
            The guild to delete the emoji on. This can be a guild object or the
            ID of an existing guild.
        emoji
            The emoji to delete. This can be a [`hikari.emojis.CustomEmoji`][]
            or the ID of an existing emoji.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing [`hikari.permissions.Permissions.MANAGE_GUILD_EXPRESSIONS`][]
            in the server.
        hikari.errors.NotFoundError
            If the guild or the emoji are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_application_emoji(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        emoji: snowflakes.SnowflakeishOr[emojis.CustomEmoji],
    ) -> emojis.KnownCustomEmoji:
        """Fetch an application emoji.

        Parameters
        ----------
        application
            The application to fetch the emoji from. This can be a [`hikari.guilds.PartialApplication`][]
            or the ID of an application.
        emoji
            The emoji to fetch. This can be a [`hikari.emojis.CustomEmoji`][]
            or the ID of an existing application emoji.


        Returns
        -------
        hikari.emojis.KnownCustomEmoji
            The requested application emoji.

        Raises
        ------
        hikari.errors.NotFoundError
            If the emoji or the application is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        hikari.errors.ForbiddenError
            If you are not allowed to access the emoji from this application.
        """

    @abc.abstractmethod
    async def fetch_application_emojis(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication]
    ) -> typing.Sequence[emojis.KnownCustomEmoji]:
        """Fetch the emojis of an application.

        Parameters
        ----------
        application
            The application to fetch the emojis from. This can be a [`hikari.guilds.PartialApplication`][]
            or the ID of an application.

        Returns
        -------
        typing.Sequence[hikari.emojis.KnownCustomEmoji]
            The requested emojis.

        Raises
        ------
        hikari.errors.NotFoundError
            If the application is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        hikari.errors.ForbiddenError
            If you are not allowed to access emojis from this application.
        """

    @abc.abstractmethod
    async def create_application_emoji(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication], name: str, image: files.Resourceish
    ) -> emojis.KnownCustomEmoji:
        """Create an application emoji.

        Parameters
        ----------
        application
            The application to create the emoji for. This can be an
            application object or the ID of an existing application.
        name
            The name for the emoji.
        image
            The 128x128 image for the emoji. Maximum upload size is 256kb.
            This can be a still or an animated image.

        Returns
        -------
        hikari.emojis.KnownCustomEmoji
            The created emoji.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value or
            if there is no more spaces for the emoji in the application.
        hikari.errors.ForbiddenError
            If you are trying to create an emoji for an application
            that is not yours.
        hikari.errors.NotFoundError
            If the application is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_application_emoji(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        emoji: snowflakes.SnowflakeishOr[emojis.CustomEmoji],
        name: str,
    ) -> emojis.KnownCustomEmoji:
        """Edit an application emoji.

        Parameters
        ----------
        application
            The application to edit the emoji on. This can be a [`hikari.guilds.PartialApplication`][]
            or the ID of an application.
        emoji
            The emoji to edit. This can be a [`hikari.emojis.CustomEmoji`][]
            or the ID of an existing emoji.
        name
            The new name for the emoji.

        Returns
        -------
        hikari.emojis.KnownCustomEmoji
            The edited emoji.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are trying to edit an emoji for an application
            that is not yours.
        hikari.errors.NotFoundError
            If the application or the emoji are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_application_emoji(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        emoji: snowflakes.SnowflakeishOr[emojis.CustomEmoji],
    ) -> None:
        """Delete an application emoji.

        Parameters
        ----------
        application
            The application to delete the emoji from. This can be a [`hikari.guilds.PartialApplication`][]
            or the ID of an application.
        emoji
            The emoji to delete. This can be a [`hikari.emojis.CustomEmoji`][]
            or the ID of an existing emoji.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are trying to edit an emoji for an application
            that is not yours.
        hikari.errors.NotFoundError
            If the application or the emoji are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_available_sticker_packs(self) -> typing.Sequence[stickers_.StickerPack]:
        """Fetch the available sticker packs.

        Returns
        -------
        typing.Sequence[hikari.stickers.StickerPack]
            The available sticker packs.

        Raises
        ------
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_sticker(
        self, sticker: snowflakes.SnowflakeishOr[stickers_.PartialSticker]
    ) -> stickers_.GuildSticker | stickers_.StandardSticker:
        """Fetch a sticker.

        Parameters
        ----------
        sticker
            The sticker to fetch. This can be a sticker object or the
            ID of an existing sticker.

        Returns
        -------
        typing.Union[hikari.stickers.GuildSticker, hikari.stickers.StandardSticker]
            The requested sticker.

        Raises
        ------
        hikari.errors.NotFoundError
            If the sticker is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_stickers(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[stickers_.GuildSticker]:
        """Fetch a standard sticker.

        Parameters
        ----------
        guild
            The guild to request stickers for. This can be a guild object or the
            ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.stickers.GuildSticker]
            The requested stickers.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the server.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_sticker(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        sticker: snowflakes.SnowflakeishOr[stickers_.PartialSticker],
    ) -> stickers_.GuildSticker:
        """Fetch a guild sticker.

        Parameters
        ----------
        guild
            The guild the sticker is in. This can be a guild object or the
            ID of an existing guild.
        sticker
            The sticker to fetch. This can be a sticker object or the
            ID of an existing sticker.

        Returns
        -------
        hikari.stickers.GuildSticker
            The requested sticker.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the server.
        hikari.errors.NotFoundError
            If the guild or the sticker are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_sticker(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        tag: str,
        image: files.Resourceish,
        *,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> stickers_.GuildSticker:
        """Create a sticker in a guild.

        Parameters
        ----------
        guild
            The guild to create the sticker on. This can be a guild object or the
            ID of an existing guild.
        name
            The name for the sticker.
        tag
            The tag for the sticker.
        image
            The 320x320 image for the sticker. Maximum upload size is 500kb.
            This can be a still PNG, an animated PNG, a Lottie, or a GIF.

            !!! note
                Lottie support is only available for verified and partnered
                servers.
        description
            If provided, the description of the sticker.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.stickers.GuildSticker
            The created sticker.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value or
            if there are no more spaces for the sticker in the guild.
        hikari.errors.ForbiddenError
            If you are missing [`hikari.permissions.Permissions.MANAGE_GUILD_EXPRESSIONS`][]
            in the server.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_sticker(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        sticker: snowflakes.SnowflakeishOr[stickers_.PartialSticker],
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        tag: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> stickers_.GuildSticker:
        """Edit a sticker in a guild.

        Parameters
        ----------
        guild
            The guild to edit the sticker on. This can be a guild object or the
            ID of an existing guild.
        sticker
            The sticker to edit. This can be a sticker object or the ID of an
            existing sticker.
        name
            If provided, the new name for the sticker.
        description
            If provided, the new description for the sticker.
        tag
            If provided, the new sticker tag.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.stickers.GuildSticker
            The edited sticker.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing [`hikari.permissions.Permissions.MANAGE_GUILD_EXPRESSIONS`][]
            in the server.
        hikari.errors.NotFoundError
            If the guild or the sticker are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_sticker(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        sticker: snowflakes.SnowflakeishOr[stickers_.PartialSticker],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete a sticker in a guild.

        Parameters
        ----------
        guild
            The guild to delete the sticker on. This can be a guild object or
            the ID of an existing guild.
        sticker
            The sticker to delete. This can be a sticker object or the ID
            of an existing sticker.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing [`hikari.permissions.Permissions.MANAGE_GUILD_EXPRESSIONS`][]
            in the server.
        hikari.errors.NotFoundError
            If the guild or the sticker are not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> guilds.RESTGuild:
        """Fetch a guild.

        Parameters
        ----------
        guild
            The guild to fetch. This can be the object
            or the ID of an existing guild.

        Returns
        -------
        hikari.guilds.RESTGuild
            The requested guild.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_preview(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> guilds.GuildPreview:
        """Fetch a guild preview.

        !!! note
            This will only work for guilds you are a part of or are public.

        Parameters
        ----------
        guild
            The guild to fetch the preview of. This can be a
            guild object or the ID of an existing guild.

        Returns
        -------
        hikari.guilds.GuildPreview
            The requested guild preview.

        Raises
        ------
        hikari.errors.NotFoundError
            If the guild is not found or you are not part of the guild.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_guild(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        verification_level: undefined.UndefinedOr[guilds.GuildVerificationLevel] = undefined.UNDEFINED,
        default_message_notifications: undefined.UndefinedOr[
            guilds.GuildMessageNotificationsLevel
        ] = undefined.UNDEFINED,
        explicit_content_filter_level: undefined.UndefinedOr[
            guilds.GuildExplicitContentFilterLevel
        ] = undefined.UNDEFINED,
        afk_channel: undefined.UndefinedOr[
            snowflakes.SnowflakeishOr[channels_.GuildVoiceChannel]
        ] = undefined.UNDEFINED,
        afk_timeout: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        icon: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        owner: undefined.UndefinedOr[snowflakes.SnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
        splash: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        banner: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        system_channel: undefined.UndefinedNoneOr[
            snowflakes.SnowflakeishOr[channels_.GuildTextChannel]
        ] = undefined.UNDEFINED,
        rules_channel: undefined.UndefinedNoneOr[
            snowflakes.SnowflakeishOr[channels_.GuildTextChannel]
        ] = undefined.UNDEFINED,
        public_updates_channel: undefined.UndefinedNoneOr[
            snowflakes.SnowflakeishOr[channels_.GuildTextChannel]
        ] = undefined.UNDEFINED,
        preferred_locale: undefined.UndefinedOr[str | locales.Locale] = undefined.UNDEFINED,
        features: undefined.UndefinedOr[typing.Sequence[guilds.GuildFeature]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.RESTGuild:
        """Edit a guild.

        Parameters
        ----------
        guild
            The guild to edit. This may be the object
            or the ID of an existing guild.
        name
            If provided, the new name for the guild.
        verification_level
            If provided, the new verification level.
        default_message_notifications
            If provided, the new default message notifications level.
        explicit_content_filter_level
            If provided, the new explicit content filter level.
        afk_channel
            If provided, the new afk channel. Requires `afk_timeout` to
            be set to work.
        afk_timeout
            If provided, the new afk timeout.
        icon
            If provided, the new guild icon. Must be a 1024x1024 image or can be
            an animated gif when the guild has the [`hikari.guilds.GuildFeature.ANIMATED_ICON`][] feature.
        owner
            If provided, the new guild owner.

            !!! warning
                You need to be the owner of the server to use this.
        splash
            If provided, the new guild splash. Must be a 16:9 image and the
            guild must have the [`hikari.guilds.GuildFeature.INVITE_SPLASH`][] feature.
        banner
            If provided, the new guild banner. Must be a 16:9 image and the
            guild must have the [`hikari.guilds.GuildFeature.BANNER`][] feature.
        system_channel
            If provided, the new system channel.
        rules_channel
            If provided, the new rules channel.
        public_updates_channel
            If provided, the new public updates channel.
        preferred_locale
            If provided, the new preferred locale.
        features
            If provided, the guild features to be enabled. Features not provided will be disabled.

            .. warning::
                At the time of writing, Discord ignores non-`mutable features
                <https://discord.com/developers/docs/resources/guild#guild-object-mutable-guild-features>`_.
                This behaviour can change in the future. You should refer to the
                aforementioned link for the most up-to-date information, and
                only supply mutable features.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.RESTGuild
            The edited guild.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value. Or
            you are missing the
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission or if you tried to
            pass ownership without being the server owner.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def set_guild_incident_actions(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        invites_disabled_until: datetime.datetime | None = None,
        dms_disabled_until: datetime.datetime | None = None,
    ) -> guilds.GuildIncidents:
        """Set the incident actions for a guild.

        !!! warning
            This endpoint will reset any previous security measures if not specified.
            This is a Discord limitation.

        Parameters
        ----------
        guild
            The guild to set the incident actions for. This may be the object
            or the ID of an existing guild.
        invites_disabled_until
            The datetime when invites will be enabled again.

            If [`None`][], invites will be enabled again immediately.

            !!! note
                If [`hikari.guilds.GuildFeature.INVITES_DISABLED`][] is active, this value will be ignored.
        dms_disabled_until
            The datetime when direct messages between non-friend guild
            members will be enabled again.

            If [`None`][], direct messages will be enabled again immediately.

        Returns
        -------
        hikari.guilds.GuildIncidents
            A guild incidents object with the updated incident actions.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you do not have at least one of the following permissions:
            - [`hikari.permissions.Permissions.ADMINISTRATOR`][]
            - [`hikari.permissions.Permissions.KICK_MEMBERS`][]
            - [`hikari.permissions.Permissions.MODERATE_MEMBERS`][]
            - [`hikari.permissions.Permissions.BAN_MEMBERS`][]
            - [`hikari.permissions.Permissions.MANAGE_GUILD`][]
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_guild(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> None:
        """Delete a guild.

        Parameters
        ----------
        guild
            The guild to delete. This may be the object or
            the ID of an existing guild.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not the owner of the guild.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If you own the guild or if you are not in it.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_channels(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[channels_.GuildChannel]:
        """Fetch the channels in a guild.

        Parameters
        ----------
        guild
            The guild to fetch the channels from. This may be the
            object or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.channels.GuildChannel]
            The requested channels.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_text_channel(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        category: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.GuildCategory]] = undefined.UNDEFINED,
        default_auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildTextChannel:
        """Create a text channel in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channels name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the channel (relative to the
            category, if any).
        topic
            If provided, the channels topic. Maximum 1024 characters.
        nsfw
            If provided, whether to mark the channel as NSFW.
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        permission_overwrites
            If provided, the permission overwrites for the channel.
        category
            The category to create the channel under. This may be the
            object or the ID of an existing category.
        default_auto_archive_duration
            If provided, the auto archive duration Discord's end user client
            should default to when creating threads in this channel.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildTextChannel
            The created channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_news_channel(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        category: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.GuildCategory]] = undefined.UNDEFINED,
        default_auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildNewsChannel:
        """Create a news channel in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channels name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the channel (relative to the
            category, if any).
        topic
            If provided, the channels topic. Maximum 1024 characters.
        nsfw
            If provided, whether to mark the channel as NSFW.
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        permission_overwrites
            If provided, the permission overwrites for the channel.
        category
            The category to create the channel under. This may be the
            object or the ID of an existing category.
        default_auto_archive_duration
            If provided, the auto archive duration Discord's end user client
            should default to when creating threads in this channel.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildNewsChannel
            The created channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_forum_channel(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        category: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.GuildCategory]] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_thread_rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_forum_layout: undefined.UndefinedOr[channels_.ForumLayoutType | int] = undefined.UNDEFINED,
        default_sort_order: undefined.UndefinedOr[channels_.ForumSortOrderType | int] = undefined.UNDEFINED,
        available_tags: undefined.UndefinedOr[typing.Sequence[channels_.ForumTag]] = undefined.UNDEFINED,
        default_reaction_emoji: str
        | emojis.Emoji
        | undefined.UndefinedType
        | snowflakes.Snowflake = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildForumChannel:
        """Create a forum channel in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channels name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the category.
        category
            The category to create the channel under. This may be the
            object or the ID of an existing category.
        permission_overwrites
            If provided, the permission overwrites for the category.
        topic
            If provided, the channels topic. Maximum 1024 characters.
        nsfw
            If provided, whether to mark the channel as NSFW.
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        default_auto_archive_duration
            If provided, the auto archive duration Discord's end user client
            should default to when creating threads in this channel.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        default_thread_rate_limit_per_user
            If provided, the ratelimit that should be set in threads created
            from the forum.
        default_forum_layout
            If provided, the default forum layout to show in the client.
        default_sort_order
            If provided, the default sort order to show in the client.
        available_tags
            If provided, the available tags to select from when creating a thread.
        default_reaction_emoji
            If provided, the new default reaction emoji for threads created in a forum channel.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildForumChannel
            The created forum channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_media_channel(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        category: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.GuildCategory]] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_thread_rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        default_forum_layout: undefined.UndefinedOr[channels_.ForumLayoutType | int] = undefined.UNDEFINED,
        default_sort_order: undefined.UndefinedOr[channels_.ForumSortOrderType | int] = undefined.UNDEFINED,
        available_tags: undefined.UndefinedOr[typing.Sequence[channels_.ForumTag]] = undefined.UNDEFINED,
        default_reaction_emoji: str
        | emojis.Emoji
        | undefined.UndefinedType
        | snowflakes.Snowflake = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildMediaChannel:
        """Create a media channel in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channels name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the category.
        category
            The category to create the channel under. This may be the
            object or the ID of an existing category.
        permission_overwrites
            If provided, the permission overwrites for the category.
        topic
            If provided, the channels topic. Maximum 1024 characters.
        nsfw
            If provided, whether to mark the channel as NSFW.
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        default_auto_archive_duration
            If provided, the auto archive duration Discord's end user client
            should default to when creating threads in this channel.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        default_thread_rate_limit_per_user
            If provided, the ratelimit that should be set in threads created
            from the forum.
        default_forum_layout
            If provided, the default forum layout to show in the client.
        default_sort_order
            If provided, the default sort order to show in the client.
        available_tags
            If provided, the available tags to select from when creating a thread.
        default_reaction_emoji
            If provided, the new default reaction emoji for threads created in the media channel.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildMediaChannel
            The created media channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_voice_channel(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        video_quality_mode: undefined.UndefinedOr[channels_.VideoQualityMode | int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        region: undefined.UndefinedOr[voices.VoiceRegion | str] = undefined.UNDEFINED,
        category: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.GuildCategory]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildVoiceChannel:
        """Create a voice channel in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channels name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the channel (relative to the
            category, if any).
        user_limit
            If provided, the maximum users in the channel at once.
            Must be between 0 and 99 with 0 meaning no limit.
        bitrate
            If provided, the bitrate for the channel. Must be
            between 8000 and 96000 or 8000 and 128000 for VIP
            servers.
        video_quality_mode
            If provided, the new video quality mode for the channel.
        permission_overwrites
            If provided, the permission overwrites for the channel.
        region
            If provided, the voice region to for this channel. Passing
            [`None`][] here will set it to "auto" mode where the used
            region will be decided based on the first person who connects to it
            when it's empty.
        category
            The category to create the channel under. This may be the
            object or the ID of an existing category.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildVoiceChannel
            The created channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_stage_channel(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        region: undefined.UndefinedOr[voices.VoiceRegion | str] = undefined.UNDEFINED,
        category: undefined.UndefinedOr[snowflakes.SnowflakeishOr[channels_.GuildCategory]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildStageChannel:
        """Create a stage channel in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channel's name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the channel (relative to the
            category, if any).
        user_limit
            If provided, the maximum users in the channel at once.
            Must be between 0 and 99 with 0 meaning no limit.
        bitrate
            If provided, the bitrate for the channel. Must be
            between 8000 and 96000 or 8000 and 128000 for VIP
            servers.
        permission_overwrites
            If provided, the permission overwrites for the channel.
        region
            If provided, the voice region to for this channel. Passing
            [`None`][] here will set it to "auto" mode where the used
            region will be decided based on the first person who connects to it
            when it's empty.
        category
            The category to create the channel under. This may be the
            object or the ID of an existing category.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildStageChannel
            The created channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_guild_category(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Sequence[channels_.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildCategory:
        """Create a category in a guild.

        Parameters
        ----------
        guild
            The guild to create the channel in. This may be the
            object or the ID of an existing guild.
        name
            The channels name. Must be between 2 and 1000 characters.
        position
            If provided, the position of the category.
        permission_overwrites
            If provided, the permission overwrites for the category.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildCategory
            The created category.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_message_thread(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PermissibleGuildChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        name: str,
        /,
        *,
        # While there is a "default archive duration" setting this doesn't seem to effect this context
        # since it always defaults to 1440 minutes if auto_archive_duration is left undefined.
        auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = datetime.timedelta(days=1),
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildPublicThread | channels_.GuildNewsThread:
        """Create a public or news thread on a message in a guild channel.

        !!! note
            This call may create a public or news thread dependent on the
            target channel's type and cannot create private threads.

        Parameters
        ----------
        channel
            Object or ID of the guild news or text channel to create a public thread in.
        message
            Object or ID of the message to attach the created thread to.
        name
            Name of the thread channel.
        auto_archive_duration
            If provided, how long the thread should remain inactive until it's archived.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        typing.Union[hikari.channels.GuildPublicThread, hikari.channels.GuildNewsThread]
            The created public or news thread channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.CREATE_PUBLIC_THREADS`][] permission or if you
            can't send messages in the target channel.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_thread(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PermissibleGuildChannel],
        type: channels_.ChannelType | int,
        name: str,
        /,
        *,
        # While there is a "default archive duration" setting this doesn't seem to effect this context
        # since it always defaults to 1440 minutes if auto_archive_duration is left undefined.
        auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = datetime.timedelta(days=1),
        invitable: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildThreadChannel:
        """Create a thread in a guild channel.

        !!! warning
            Private and public threads can only be made in guild text channels,
            and news threads can only be made in guild news channels.

        Parameters
        ----------
        channel
            Object or ID of the guild news or text channel to create a thread in.
        type
            The thread type to create.
        name
            Name of the thread channel.
        auto_archive_duration
            If provided, how long the thread should remain inactive until it's archived.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        invitable
            If provided, whether non-moderators should be able to add other non-moderators to the thread.

            This only applies to private threads.
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildThreadChannel
            The created thread channel.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.CREATE_PUBLIC_THREADS`][] permission or if you
            can't send messages in the target channel.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_forum_post(  # noqa: PLR0913
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PermissibleGuildChannel],
        name: str,
        /,
        # Message arguments
        content: undefined.UndefinedOr[typing.Any] = undefined.UNDEFINED,
        *,
        attachment: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        attachments: undefined.UndefinedOr[typing.Sequence[files.Resourceish]] = undefined.UNDEFINED,
        component: undefined.UndefinedOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedOr[typing.Sequence[special_endpoints.ComponentBuilder]] = undefined.UNDEFINED,
        embed: undefined.UndefinedOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        poll: undefined.UndefinedOr[special_endpoints.PollBuilder] = undefined.UNDEFINED,
        sticker: undefined.UndefinedOr[snowflakes.SnowflakeishOr[stickers_.PartialSticker]] = undefined.UNDEFINED,
        stickers: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[stickers_.PartialSticker]
        ] = undefined.UNDEFINED,
        tts: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_reply: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
        flags: undefined.UndefinedType | int | messages_.MessageFlag = undefined.UNDEFINED,
        # Channel arguments
        auto_archive_duration: undefined.UndefinedOr[time.Intervalish] = datetime.timedelta(days=1),
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        tags: undefined.UndefinedOr[typing.Sequence[snowflakes.Snowflake]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> channels_.GuildPublicThread:
        """Create a post in a forum or media channel.

        Parameters
        ----------
        channel
            Object or ID of the forum or media channel to create a post in.
        name
            Name of the post.
        content
            If provided, the message contents. If
            [`hikari.undefined.UNDEFINED`][], then nothing will be sent
            in the content. Any other value here will be cast to a
            [`str`][].

            If this is a [`hikari.embeds.Embed`][] and no `embed` nor `embeds` kwarg
            is provided, then this will instead update the embed. This allows
            for simpler syntax when sending an embed alone.

            Likewise, if this is a [`hikari.files.Resource`][], then the
            content is instead treated as an attachment if no `attachment` and
            no `attachments` kwargs are provided.
        attachment
            If provided, the message attachment. This can be a resource,
            or string of a path on your computer or a URL.

            Attachments can be passed as many different things, to aid in
            convenience.

            - If a [`pathlib.PurePath`][] or [`str`][] to a valid URL, the
                resource at the given URL will be streamed to Discord when
                sending the message. Subclasses of
                [`hikari.files.WebResource`][] such as
                [`hikari.files.URL`][],
                [`hikari.messages.Attachment`][],
                [`hikari.emojis.Emoji`][],
                [`hikari.embeds.EmbedResource`][], etc will also be uploaded this way.
                This will use bit-inception, so only a small percentage of the
                resource will remain in memory at any one time, thus aiding in
                scalability.
            - If a [`hikari.files.Bytes`][] is passed, or a [`str`][]
                that contains a valid data URI is passed, then this is uploaded
                with a randomized file name if not provided.
            - If a [`hikari.files.File`][], [`pathlib.PurePath`][] or
                [`str`][] that is an absolute or relative path to a file
                on your file system is passed, then this resource is uploaded
                as an attachment using non-blocking code internally and streamed
                using bit-inception where possible. This depends on the
                type of [`concurrent.futures.Executor`][] that is being used for
                the application (default is a thread pool which supports this
                behaviour).
        attachments
            If provided, the message attachments. These can be resources, or
            strings consisting of paths on your computer or URLs.
        component
            If provided, builder object of the component to include in this message.
        components
            If provided, a sequence of the component builder objects to include
            in this message.
        embed
            If provided, the message embed.
        embeds
            If provided, the message embeds.
        poll
            If provided, the message poll.
        sticker
            If provided, the object or ID of a sticker to send on the message.

            As of writing, bots can only send custom stickers from the current guild.
        stickers
            If provided, a sequence of the objects and IDs of up to 3 stickers
            to send on the message.

            As of writing, bots can only send custom stickers from the current guild.
        tts
            If provided, whether the message will be read out by a screen
            reader using Discord's TTS (text-to-speech) system.
        mentions_everyone
            If provided, whether the message should parse @everyone/@here
            mentions.
        mentions_reply
            If provided, whether to mention the author of the message
            that is being replied to.

            This will not do anything if not being used with `reply`.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If provided, and [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If provided, and [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.
        flags
            If provided, optional flags to set on the message. If
            [`hikari.undefined.UNDEFINED`][], then nothing is changed.

            Note that some flags may not be able to be set. Currently the only
            flags that can be set are [`hikari.messages.MessageFlag.NONE`][] and
            [`hikari.messages.MessageFlag.SUPPRESS_EMBEDS`][].
        auto_archive_duration
            If provided, how long the post should remain inactive until it's archived.

            This should be either 60, 1440, 4320 or 10080 minutes and, as of
            writing, ignores the parent channel's set default_auto_archive_duration
            when passed as [`hikari.undefined.UNDEFINED`][].
        rate_limit_per_user
            If provided, the amount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        tags
            If provided, the tags to add to the created post.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.channels.GuildPublicThread
            The created post.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.SEND_MESSAGES`][]
            permission in the channel.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def join_thread(self, channel: snowflakes.SnowflakeishOr[channels_.GuildTextChannel], /) -> None:
        """Join a thread channel.

        Parameters
        ----------
        channel
            Object or ID of the thread channel to join.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you cannot join this thread.
        hikari.errors.NotFoundError
            If the thread channel does not exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def add_thread_member(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildThreadChannel],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        /,
    ) -> None:
        """Add a user to a thread channel.

        Parameters
        ----------
        channel
            Object or ID of the thread channel to add a member to.
        user
            Object or ID of the user to add to the thread.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you cannot add a user to this thread.
        hikari.errors.NotFoundError
            If the thread channel doesn't exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def leave_thread(self, channel: snowflakes.SnowflakeishOr[channels_.GuildThreadChannel], /) -> None:
        """Leave a thread channel.

        Parameters
        ----------
        channel
            Object or ID of the thread channel to leave.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.NotFoundError
            If you're not in the thread or it doesn't exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def remove_thread_member(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildThreadChannel],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        /,
    ) -> None:
        """Remove a user from a thread.

        Parameters
        ----------
        channel
            Object or ID of the thread channel to remove a user from.
        user
            Object or ID of the user to remove from the thread.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you cannot remove this user from the thread.
        hikari.errors.NotFoundError
            If the thread channel or member doesn't exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_thread_member(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildThreadChannel],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        /,
    ) -> channels_.ThreadMember:
        """Fetch a thread member.

        Parameters
        ----------
        channel
            Object or ID of the thread channel to fetch the member of.
        user
            Object or ID of the user to fetch the thread member of.

        Returns
        -------
        hikari.channels.ThreadMember
            The thread member.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you access the thread.
        hikari.errors.NotFoundError
            If the thread channel or member doesn't exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_thread_members(
        self, channel: snowflakes.SnowflakeishOr[channels_.GuildThreadChannel], /
    ) -> typing.Sequence[channels_.ThreadMember]:
        """Fetch a thread's members.

        Parameters
        ----------
        channel
            Object or ID of the thread channel to fetch the members of.

        Returns
        -------
        typing.Sequence[hikari.channels.ThreadMember]
            A sequence of the thread's members.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you access the thread.
        hikari.errors.NotFoundError
            If the thread channel doesn't exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_active_threads(
        self, guild: snowflakes.SnowflakeishOr[guilds.Guild], /
    ) -> typing.Sequence[channels_.GuildThreadChannel]:
        """Fetch a guild's active threads.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch the active threads of.

        Returns
        -------
        typing.Sequence[hikari.channels.GuildThreadChannel]
            A sequence of the guild's active threads.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you access the guild's active threads.
        hikari.errors.NotFoundError
            If the guild doesn't exist.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_public_archived_threads(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PermissibleGuildChannel],
        /,
        *,
        before: undefined.UndefinedOr[datetime.datetime] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[channels_.GuildNewsThread | channels_.GuildPublicThread]:
        """Fetch a channel's public archived threads.

        !!! note
            The exceptions on this endpoint will only be raised once the
            result is awaited or iterated over. Invoking this function
            itself will not raise anything.

        Parameters
        ----------
        channel
            Object or ID of the channel to fetch the archived threads of.
        before
            The date to fetch threads before.

            This is based on the thread's `archive_timestamp` field.

        Returns
        -------
        hikari.iterators.LazyIterator[typing.Union[hikari.channels.GuildNewsChannel, hikari.channels.GuildPublicThread]]
            An iterator to fetch the threads.

            !!! note
                This call is not a coroutine function, it returns a special type of
                lazy iterator that will perform API calls as you iterate across it.
                See [`hikari.iterators`][] for the full API for this iterator type.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you cannot access the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_private_archived_threads(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PermissibleGuildChannel],
        /,
        *,
        before: undefined.UndefinedOr[datetime.datetime] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[channels_.GuildPrivateThread]:
        """Fetch a channel's private archived threads.

        !!! note
            The exceptions on this endpoint will only be raised once the
            result is awaited or iterated over. Invoking this function
            itself will not raise anything.

        Parameters
        ----------
        channel
            Object or ID of the channel to fetch the private archived threads of.
        before
            The date to fetch threads before.

            This is based on the thread's `archive_timestamp` field.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.channels.GuildPrivateThread]
            An iterator to fetch the threads.

            !!! note
                This call is not a coroutine function, it returns a special type of
                lazy iterator that will perform API calls as you iterate across it.
                See [`hikari.iterators`][] for the full API for this iterator type.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you do not have [`hikari.permissions.Permissions.MANAGE_THREADS`][] in the target channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_joined_private_archived_threads(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.PermissibleGuildChannel],
        /,
        *,
        before: undefined.UndefinedOr[
            snowflakes.SearchableSnowflakeishOr[channels_.GuildThreadChannel]
        ] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[channels_.GuildPrivateThread]:
        """Fetch the private archived threads you have joined in a channel.

        !!! note
            The exceptions on this endpoint will only be raised once the
            result is awaited or iterated over. Invoking this function
            itself will not raise anything.

        Parameters
        ----------
        channel
            Object or ID of the channel to fetch the private archived threads of.
        before
            If provided, fetch joined threads before this snowflake. If you
            provide a datetime object, it will be transformed into a snowflake.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.channels.GuildPrivateThread]
            An iterator to fetch the threads.

            !!! note
                This call is not a coroutine function, it returns a special type of
                lazy iterator that will perform API calls as you iterate across it.
                See [`hikari.iterators`][] for the full API for this iterator type.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you cannot access the channel.
        hikari.errors.NotFoundError
            If the channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def reposition_channels(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        positions: undefined.UndefinedOr[
            typing.Mapping[int, snowflakes.SnowflakeishOr[channels_.GuildChannel]]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> special_endpoints.ChannelRepositioner:
        """Return a [`hikari.api.special_endpoints.ChannelRepositioner`][], used to reposition channels in a guild.

        See [`hikari.api.special_endpoints.ChannelRepositioner`][] for more functionality on this endpoint

        Parameters
        ----------
        guild
            The guild to reposition the channels in. This may be the
            object or the ID of an existing guild.
        positions
            A mapping of the new position to the object or the ID of an existing channel,
            relative to their parent category, if any.

            !!! note
                Instead of using the `positions` parameter, you should make
                use of the returned [`hikari.api.special_endpoints.ChannelRepositioner`][].
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_CHANNELS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.

        Returns
        -------
        hikari.api.special_endpoints.ChannelRepositioner
            The channel repositioner.

        """

    @abc.abstractmethod
    async def fetch_member(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], user: snowflakes.SnowflakeishOr[users.PartialUser]
    ) -> guilds.Member:
        """Fetch a guild member.

        Parameters
        ----------
        guild
            The guild to get the member from. This may be the
            object or the ID of an existing guild.
        user
            The user to get the member for. This may be the
            object or the ID of an existing user.

        Returns
        -------
        hikari.guilds.Member
            The requested member.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or the user are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_members(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        after: undefined.UndefinedOr[snowflakes.SnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
        limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[guilds.Member]:
        """Fetch the members from a guild.

        !!! warning
            This endpoint requires the [hikari.intents.Intents.GUILD_MEMBERS] intent
            to be enabled in the dashboard, not necessarily authenticated with it
            if using the gateway. If you don't have the intents you can use
            [`hikari.api.rest.RESTClient.search_members`][] which doesn't require
            any intents.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it,
            thus any errors documented below will happen then.

            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        guild
            The guild to fetch the members of. This may be the
            object or the ID of an existing guild.
        after
            If provided, fetch members after this snowflake. If you
            provide a datetime object, it will be transformed into a snowflake.
        limit
            The maximum number of members to fetch.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.guilds.Member]
            An iterator to fetch the members.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_my_member(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> guilds.Member:
        """Fetch the Oauth token's associated member in a guild.

        !!! warning
            This endpoint can only be used with a Bearer token. Using this
            with a Bot token will result in a [`hikari.errors.UnauthorizedError`][].

        Returns
        -------
        hikari.guilds.Member
            The associated guild member.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def search_members(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], name: str
    ) -> typing.Sequence[guilds.Member]:
        """Search the members in a guild by nickname and username.

        !!! note
            Unlike [`hikari.api.rest.RESTClient.fetch_members`][] this endpoint isn't paginated and
            therefore will return all the members in one go rather than needing
            to be asynchronously iterated over.

        Parameters
        ----------
        guild
            The object or ID of the guild to search members in.
        name
            The query to match username(s) and nickname(s) against.

        Returns
        -------
        typing.Sequence[hikari.guilds.Member]
            A sequence of the members who matched the provided `name`.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        nickname: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
        roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        mute: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        deaf: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        voice_channel: undefined.UndefinedNoneOr[
            snowflakes.SnowflakeishOr[channels_.GuildVoiceChannel]
        ] = undefined.UNDEFINED,
        communication_disabled_until: undefined.UndefinedNoneOr[datetime.datetime] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.Member:
        """Edit a guild member.

        Parameters
        ----------
        guild
            The guild to edit. This may be the object
            or the ID of an existing guild.
        user
            The user to edit. This may be the object
            or the ID of an existing user.
        nickname
            If provided, the new nick for the member. If [`None`][],
            will remove the members nick.

            Requires the [`hikari.permissions.Permissions.MANAGE_NICKNAMES`][] permission.
        roles
            If provided, the new roles for the member.

            Requires the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        mute
            If provided, the new server mute state for the member.

            Requires the [`hikari.permissions.Permissions.MUTE_MEMBERS`][] permission.
        deaf
            If provided, the new server deaf state for the member.

            Requires the [`hikari.permissions.Permissions.DEAFEN_MEMBERS`][] permission.
        voice_channel
            If provided, [`None`][] or the object or the ID of
            an existing voice channel to move the member to.
            If [`None`][], will disconnect the member from voice.

            Requires the [`hikari.permissions.Permissions.MOVE_MEMBERS`][] permission
            and the [`hikari.permissions.Permissions.CONNECT`][] permission in the
            original voice channel and the target voice channel.

            !!! note
                If the member is not in a voice channel, this will
                take no effect.
        communication_disabled_until
            If provided, the datetime when the timeout (disable communication)
            of the member expires, up to 28 days in the future, or [`None`][]
            to remove the timeout from the member.

            Requires the [`hikari.permissions.Permissions.MODERATE_MEMBERS`][] permission.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.Member
            Object of the member that was updated.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing a permission to do an action.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or the user are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_my_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        nickname: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.Member:
        """Edit the current user's member in a guild.

        Parameters
        ----------
        guild
            The guild to edit the member in. This may be the object
            or the ID of an existing guild.
        nickname
            If provided, the new nickname for the member. If
            [`None`][], will remove the members nickname.

            Requires the [`hikari.permissions.Permissions.CHANGE_NICKNAME`][] permission.
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.Member
            Object of the member that was updated.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing a permission to do an action.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def add_role_to_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        role: snowflakes.SnowflakeishOr[guilds.PartialRole],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Add a role to a member.

        Parameters
        ----------
        guild
            The guild where the member is in. This may be the
            object or the ID of an existing guild.
        user
            The user to add the role to. This may be the
            object or the ID of an existing user.
        role
            The role to add. This may be the object or the
            ID of an existing role.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild, user or role are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def remove_role_from_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        role: snowflakes.SnowflakeishOr[guilds.PartialRole],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Remove a role from a member.

        Parameters
        ----------
        guild
            The guild where the member is in. This may be the
            object or the ID of an existing guild.
        user
            The user to remove the role from. This may be the
            object or the ID of an existing user.
        role
            The role to remove. This may be the object or the
            ID of an existing role.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild, user or role are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def kick_user(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Kick a member from a guild.

        Parameters
        ----------
        guild
            The guild to kick the member from. This may be the
            object or the ID of an existing guild.
        user
            The user to kick. This may be the object
            or the ID of an existing user.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.KICK_MEMBERS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or user are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def kick_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Alias of [`hikari.api.rest.RESTClient.kick_user`][]."""

    @abc.abstractmethod
    async def ban_user(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        delete_message_seconds: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Ban the given user from this guild.

        Parameters
        ----------
        guild
            The guild to ban the member from. This may be the
            object or the ID of an existing guild.
        user
            The user to kick. This may be the object
            or the ID of an existing user.
        delete_message_seconds
            If provided, the number of seconds to delete messages for.
            This can be represented as either an int/float between 0 and 604800 (7 days), or
            a [`datetime.timedelta`][] object.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.BAN_MEMBERS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or user are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def ban_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        delete_message_seconds: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Alias of [`hikari.api.rest.RESTClient.ban_user`][]."""

    @abc.abstractmethod
    async def unban_user(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Unban a member from a guild.

        Parameters
        ----------
        guild
            The guild to unban the member from. This may be the
            object or the ID of an existing guild.
        user
            The user to unban. This may be the object
            or the ID of an existing user.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.BAN_MEMBERS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or user are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def unban_member(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        user: snowflakes.SnowflakeishOr[users.PartialUser],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Alias of [`hikari.api.rest.RESTClient.unban_user`][]."""

    @abc.abstractmethod
    async def fetch_ban(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], user: snowflakes.SnowflakeishOr[users.PartialUser]
    ) -> guilds.GuildBan:
        """Fetch the guild's ban info for a user.

        Parameters
        ----------
        guild
            The guild to fetch the ban from. This may be the
            object or the ID of an existing guild.
        user
            The user to fetch the ban of. This may be the
            object or the ID of an existing user.

        Returns
        -------
        hikari.guilds.GuildBan
            The requested ban info.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.BAN_MEMBERS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or user are not found or if the user
            is not banned.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_bans(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        /,
        *,
        newest_first: bool = False,
        start_at: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[guilds.GuildBan]:
        """Fetch the bans of a guild.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it.
            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        guild
            The guild to fetch the bans from. This may be the
            object or the ID of an existing guild.
        newest_first
            Whether to fetch the newest first or the oldest first.
        start_at
            If provided, will start at this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may also be a scheduled event object object. In this case, the
            date the object was first created will be used.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.guilds.GuildBan]
            The requested bans.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.BAN_MEMBERS`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_role(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], role: snowflakes.SnowflakeishOr[guilds.PartialRole]
    ) -> guilds.Role:
        """Fetch a single role of a guild.

        Parameters
        ----------
        guild
            The guild to fetch the role from. This may be the
            object or the ID of an existing guild.
        role
            The role to fetch. This may be the object or the
            ID of an existing role.

        Returns
        -------
        hikari.guilds.Role
            The requested role.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or the role is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_roles(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> typing.Sequence[guilds.Role]:
        """Fetch the roles of a guild.

        Parameters
        ----------
        guild
            The guild to fetch the roles from. This may be the
            object or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.guilds.Role]
            The requested roles.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_role(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        permissions: undefined.UndefinedOr[permissions_.Permissions] = permissions_.Permissions.NONE,
        color: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        colour: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        hoist: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        icon: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        unicode_emoji: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        mentionable: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.Role:
        """Create a role.

        Parameters
        ----------
        guild
            The guild to create the role in. This may be the
            object or the ID of an existing guild.
        name
            If provided, the name for the role.
        permissions
            The permissions to give the role. This will default to setting
            NO permissions if left as the default value. This is in contrast to
            default behaviour on Discord where some random permissions will
            be set by default.
        color
            If provided, the role's color.
        colour
            An alias for `color`.
        hoist
            If provided, whether to hoist the role.
        icon
            If provided, the role icon. Must be a 64x64 image under 256kb.
        unicode_emoji
            If provided, the standard emoji to set as the role icon.
        mentionable
            If provided, whether to make the role mentionable.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.Role
            The created role.

        Raises
        ------
        TypeError
            If both `color` and `colour` are specified or if both `icon` and
            `unicode_emoji` are specified.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def reposition_roles(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        positions: typing.Mapping[int, snowflakes.SnowflakeishOr[guilds.PartialRole]],
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Reposition the roles in a guild.

        Parameters
        ----------
        guild
            The guild to reposition the roles in. This may be
            the object or the ID of an existing guild.
        positions
            A mapping of the position to the role.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_role(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        role: snowflakes.SnowflakeishOr[guilds.PartialRole],
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        permissions: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        color: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        colour: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        hoist: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        icon: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        unicode_emoji: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
        mentionable: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.Role:
        """Edit a role.

        Parameters
        ----------
        guild
            The guild to edit the role in. This may be the
            object or the ID of an existing guild.
        role
            The role to edit. This may be the object or the
            ID of an existing role.
        name
            If provided, the new name for the role.
        permissions
            If provided, the new permissions for the role.
        color
            If provided, the new color for the role.
        colour
            An alias for `color`.
        hoist
            If provided, whether to hoist the role.
        icon
            If provided, the new role icon. Must be a 64x64 image
            under 256kb.
        unicode_emoji
            If provided, the new unicode emoji to set as the role icon.
        mentionable
            If provided, whether to make the role mentionable.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.Role
            The edited role.

        Raises
        ------
        TypeError
            If both `color` and `colour` are specified or if both `icon` and
            `unicode_emoji` are specified.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or role are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_role(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        role: snowflakes.SnowflakeishOr[guilds.PartialRole],
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete a role.

        Parameters
        ----------
        guild
            The guild to delete the role in. This may be the
            object or the ID of an existing guild.
        role
            The role to delete. This may be the object or the
            ID of an existing role.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_ROLES`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or role are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def estimate_guild_prune_count(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        days: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        include_roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
    ) -> int:
        """Estimate the guild prune count.

        Parameters
        ----------
        guild
            The guild to estimate the guild prune count for. This may be the object
            or the ID of an existing guild.
        days
            If provided, number of days to count prune for.
        include_roles
            If provided, the role(s) to include. By default, this endpoint will
            not count users with roles. Providing roles using this attribute
            will make members with the specified roles also get included into
            the count.

        Returns
        -------
        int
            The estimated guild prune count.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.KICK_MEMBERS`][] permission.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def begin_guild_prune(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        days: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        compute_prune_count: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        include_roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> int | None:
        """Begin the guild prune.

        Parameters
        ----------
        guild
            The guild to begin the guild prune in. This may be the object
            or the ID of an existing guild.
        days
            If provided, number of days to count prune for.
        compute_prune_count
            If provided, whether to return the prune count. This is discouraged
            for large guilds.
        include_roles
            If provided, the role(s) to include. By default, this endpoint will
            not count users with roles. Providing roles using this attribute
            will make members with the specified roles also get included into
            the count.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        typing.Optional[int]
            If `compute_prune_count` is not provided or [`True`][], the
            number of members pruned. Else [`None`][].

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.KICK_MEMBERS`][] permission.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_voice_regions(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[voices.VoiceRegion]:
        """Fetch the available voice regions for a guild.

        Parameters
        ----------
        guild
            The guild to fetch the voice regions for. This may be the object
            or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.voices.VoiceRegion]
            The available voice regions for the guild.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_invites(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[invites.InviteWithMetadata]:
        """Fetch the guild's invites.

        Parameters
        ----------
        guild
            The guild to fetch the invites for. This may be the object
            or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.invites.InviteWithMetadata]
            The invites for the guild.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_integrations(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[guilds.Integration]:
        """Fetch the guild's integrations.

        Parameters
        ----------
        guild
            The guild to fetch the integrations for. This may be the object
            or the ID of an existing guild.

        Returns
        -------
        typing.Sequence[hikari.guilds.Integration]
            The integrations for the guild.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_widget(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> guilds.GuildWidget:
        """Fetch a guilds's widget.

        Parameters
        ----------
        guild
            The guild to fetch the widget from. This can be the object
            or the ID of an existing guild.

        Returns
        -------
        hikari.guilds.GuildWidget
            The requested guild widget.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_widget(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        channel: undefined.UndefinedNoneOr[snowflakes.SnowflakeishOr[channels_.GuildChannel]] = undefined.UNDEFINED,
        enabled: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.GuildWidget:
        """Fetch a guilds's widget.

        Parameters
        ----------
        guild
            The guild to edit the widget in. This can be the object
            or the ID of an existing guild.
        channel
            If provided, the channel to set the widget to. If [`None`][],
            will not set to any.
        enabled
            If provided, whether to enable the widget.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.GuildWidget
            The edited guild widget.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_welcome_screen(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> guilds.WelcomeScreen:
        """Fetch a guild's welcome screen.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch the welcome screen for.

        Returns
        -------
        hikari.guilds.WelcomeScreen
            The requested welcome screen.

        Raises
        ------
        hikari.errors.NotFoundError
            If the guild is not found or the welcome screen has never been set
            for this guild (if the welcome screen has been set for a guild
            before and then disabled you should still be able to fetch it).
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_welcome_screen(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        description: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
        enabled: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        channels: undefined.UndefinedNoneOr[typing.Sequence[guilds.WelcomeChannel]] = undefined.UNDEFINED,
    ) -> guilds.WelcomeScreen:
        """Edit the welcome screen of a community guild.

        Parameters
        ----------
        guild
            ID or object of the guild to edit the welcome screen for.
        description
            If provided, the description to set for the guild's welcome screen.
            This may be [`None`][] to unset the description.
        enabled
            If provided, Whether the guild's welcome screen should be enabled.
        channels
            If provided, a sequence of up to 5 public channels to set in this
            guild's welcome screen. This may be passed as [`None`][] to
            remove all welcome channels

            !!! note
                Custom emojis may only be included in a guild's welcome channels
                if it's boost status is tier 2 or above.

        Returns
        -------
        hikari.guilds.WelcomeScreen
            The edited guild welcome screen.

        Raises
        ------
        hikari.errors.BadRequestError
            If more than 5 welcome channels are provided or if a custom emoji
            is included on a welcome channel in a guild that doesn't have tier
            2 of above boost status or if a private channel is included as a
            welcome channel.
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][] permission, are not part of
            the guild or the guild doesn't have access to the community welcome
            screen feature.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_onboarding(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> guilds.GuildOnboarding:
        """Fetch a guild's onboarding object.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch the onboarding object for.

        Returns
        -------
        hikari.guilds.GuildOnboarding
            The requested onboarding object.

        Raises
        ------
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_guild_onboarding(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        default_channel_ids: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[channels_.GuildChannel]
        ] = undefined.UNDEFINED,
        enabled: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mode: undefined.UndefinedOr[guilds.GuildOnboardingMode] = undefined.UNDEFINED,
        prompts: undefined.UndefinedOr[
            typing.Sequence[special_endpoints.GuildOnboardingPromptBuilder]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> guilds.GuildOnboarding:
        """Edit a guilds onboarding flow.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch the onboarding object for.
        default_channel_ids
            Sequence of channel ids that a user get opted into by default.
        enabled
            If the onboarding flow should be enabled in this guild.
        mode
            The onboarding mode for the guild. For further information look at [`hikari.guilds.GuildOnboardingMode`][].
        prompts
            The prompts of the onboarding flow.
            For further information look at [`hikari.api.special_endpoints.GuildOnboardingPromptBuilder`][].
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.guilds.GuildOnboarding
            The requested onboarding object.

        Raises
        ------
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_vanity_url(self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]) -> invites.VanityURL:
        """Fetch a guild's vanity url.

        Parameters
        ----------
        guild
            The guild to fetch the vanity url from. This can
            be the object or the ID of an existing guild.

        Returns
        -------
        hikari.invites.VanityURL
            The requested invite.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_template(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        *,
        description: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
    ) -> templates.Template:
        """Create a guild template.

        Parameters
        ----------
        guild
            The guild to create a template from.
        name
            The name to use for the created template.
        description
            The description to set for the template.

        Returns
        -------
        hikari.templates.Template
            The object of the created template.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found or you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][]
            permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_template(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], template: str | templates.Template
    ) -> templates.Template:
        """Delete a guild template.

        Parameters
        ----------
        guild
            The guild to delete a template in.
        template
            Object or string code of the template to delete.

        Returns
        -------
        hikari.templates.Template
            The deleted template's object.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found or you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][]
            permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_template(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        template: templates.Template | str,
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        description: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
    ) -> templates.Template:
        """Modify a guild template.

        Parameters
        ----------
        guild
            The guild to edit a template in.
        template
            Object or string code of the template to modify.
        name
            The name to set for this template.
        description
            The description to set for the template.

        Returns
        -------
        hikari.templates.Template
            The object of the edited template.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found or you are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][]
            permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_template(self, template: str | templates.Template) -> templates.Template:
        """Fetch a guild template.

        Parameters
        ----------
        template
            The object or string code of the template to fetch.

        Returns
        -------
        hikari.templates.Template
            The object of the found template.

        Raises
        ------
        hikari.errors.NotFoundError
            If the template was not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_guild_templates(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild]
    ) -> typing.Sequence[templates.Template]:
        """Fetch the templates for a guild.

        Parameters
        ----------
        guild
            The object or ID of the guild to get the templates for.

        Returns
        -------
        typing.Sequence[hikari.templates.Template]
            A sequence of the found template objects.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild.
        hikari.errors.NotFoundError
            If the guild is not found or are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][]
            permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def sync_guild_template(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], template: str | templates.Template
    ) -> templates.Template:
        """Create a guild template.

        Parameters
        ----------
        guild
            The guild to sync a template in.
        template
            Object or code of the template to sync.

        Returns
        -------
        hikari.templates.Template
            The object of the synced template.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you are not part of the guild or are missing the [`hikari.permissions.Permissions.MANAGE_GUILD`][]
            permission.
        hikari.errors.NotFoundError
            If the guild or template is not found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def slash_command_builder(self, name: str, description: str) -> special_endpoints.SlashCommandBuilder:
        r"""Create a command builder to use in [`hikari.api.rest.RESTClient.set_application_commands`][].

        Parameters
        ----------
        name
            The command's name. This should match the regex `^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$` in
            Unicode mode and be lowercase.
        description
            The description to set for the command if this is a slash command.
            This should be inclusively between 1-100 characters in length.

        Returns
        -------
        hikari.api.special_endpoints.SlashCommandBuilder
            The created command builder object.
        """

    @abc.abstractmethod
    def context_menu_command_builder(
        self, type: commands.CommandType | int, name: str
    ) -> special_endpoints.ContextMenuCommandBuilder:
        """Create a command builder to use in [`hikari.api.rest.RESTClient.set_application_commands`][].

        Parameters
        ----------
        type
            The commands's type.
        name
            The command's name.

        Returns
        -------
        hikari.api.special_endpoints.ContextMenuCommandBuilder
            The created command builder object.
        """

    @abc.abstractmethod
    async def fetch_application_command(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        command: snowflakes.SnowflakeishOr[commands.PartialCommand],
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> commands.PartialCommand:
        """Fetch a command set for an application.

        Parameters
        ----------
        application
            Object or ID of the application to fetch a command for.
        command
            Object or ID of the command to fetch.
        guild
            Object or ID of the guild to fetch the command for. If left as
            [`hikari.undefined.UNDEFINED`][] then this will return a global command,
            otherwise this will return a command made for the specified guild.

        Returns
        -------
        hikari.commands.PartialCommand
            Object of the fetched command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the target command.
        hikari.errors.NotFoundError
            If the command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_application_commands(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> typing.Sequence[commands.PartialCommand]:
        """Fetch the commands set for an application.

        Parameters
        ----------
        application
            Object or ID of the application to fetch the commands for.
        guild
            Object or ID of the guild to fetch the commands for. If left as
            [`hikari.undefined.UNDEFINED`][] then this will only return the global
            commands, otherwise this will only return the commands set exclusively
            for the specific guild.

        Returns
        -------
        typing.Sequence[hikari.commands.PartialCommand]
            A sequence of the commands declared for the provided application.
            This will exclusively either contain the commands set for a specific
            guild if `guild` is provided or the global commands if not.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the target guild.
        hikari.errors.NotFoundError
            If the provided application isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_slash_command(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        name: str,
        description: str,
        *,
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
        options: undefined.UndefinedOr[typing.Sequence[commands.CommandOption]] = undefined.UNDEFINED,
        name_localizations: undefined.UndefinedOr[typing.Mapping[locales.Locale | str, str]] = undefined.UNDEFINED,
        description_localizations: undefined.UndefinedOr[
            typing.Mapping[locales.Locale | str, str]
        ] = undefined.UNDEFINED,
        default_member_permissions: undefined.UndefinedType | int | permissions_.Permissions = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> commands.SlashCommand:
        r"""Create an application slash command.

        Parameters
        ----------
        application
            Object or ID of the application to create a command for.
        name
            The command's name. This should match the regex
            `^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$` in Unicode mode and
            be lowercase.
        description
            The description to set for the command.
            This should be inclusively between 1-100 characters in length.
        guild
            Object or ID of the specific guild this should be made for.
            If left as [`hikari.undefined.UNDEFINED`][] then this call will create
            a global command rather than a guild specific one.
        options
            A sequence of up to 10 options for this command.
        name_localizations
            The name localizations for this command.
        description_localizations
            The description localizations for this command.
        default_member_permissions
            Member permissions necessary to utilize this command by default.

            If `0`, then it will be available for all members. Note that this doesn't affect
            administrators of the guild and overwrites.
        nsfw
            Whether this command should be age-restricted.

        Returns
        -------
        hikari.commands.SlashCommand
            Object of the created command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands.
        hikari.errors.NotFoundError
            If the provided application isn't found.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_context_menu_command(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        type: commands.CommandType | int,
        name: str,
        *,
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
        name_localizations: undefined.UndefinedOr[typing.Mapping[locales.Locale | str, str]] = undefined.UNDEFINED,
        default_member_permissions: undefined.UndefinedType | int | permissions_.Permissions = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> commands.ContextMenuCommand:
        r"""Create an application context menu command.

        Parameters
        ----------
        application
            Object or ID of the application to create a command for.
        type
            The type of menu command to make.

            Only USER and MESSAGE are valid here.
        name
            The command's name.
        guild
            Object or ID of the specific guild this should be made for.
            If left as [`hikari.undefined.UNDEFINED`][] then this call will create
            a global command rather than a guild specific one.
        name_localizations
            The name localizations for this command.
        default_member_permissions
            Member permissions necessary to utilize this command by default.

            If `0`, then it will be available for all members. Note that this doesn't affect
            administrators of the guild and overwrites.
        nsfw
            Whether this command should be age-restricted.

        Returns
        -------
        hikari.commands.ContextMenuCommand
            Object of the created command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands.
        hikari.errors.NotFoundError
            If the provided application isn't found.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def set_application_commands(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        commands: typing.Sequence[special_endpoints.CommandBuilder],
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> typing.Sequence[commands.PartialCommand]:
        """Set the commands for an application.

        !!! warning
            Any existing commands not included in the provided commands array
            will be deleted.

        Parameters
        ----------
        application
            Object or ID of the application to create a command for.
        commands
            A sequence of up to 100 initialised command builder objects of the
            commands to set for this the application.
        guild
            Object or ID of the specific guild to set the commands for.
            If left as [`hikari.undefined.UNDEFINED`][] then this set the global
            commands rather than guild specific commands.

        Returns
        -------
        typing.Sequence[hikari.commands.PartialCommand]
            A sequence of the set command objects.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands.
        hikari.errors.NotFoundError
            If the provided application isn't found.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_application_command(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        command: snowflakes.SnowflakeishOr[commands.PartialCommand],
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        options: undefined.UndefinedOr[typing.Sequence[commands.CommandOption]] = undefined.UNDEFINED,
        default_member_permissions: undefined.UndefinedType | int | permissions_.Permissions = undefined.UNDEFINED,
    ) -> commands.PartialCommand:
        """Edit a registered application command.

        Parameters
        ----------
        application
            Object or ID of the application to edit a command for.
        command
            Object or ID of the command to modify.
        guild
            Object or ID of the guild to edit a command for if this is a guild
            specific command. Leave this as [`hikari.undefined.UNDEFINED`][] to delete
            a global command.
        name
            The name to set for the command. Leave as [`hikari.undefined.UNDEFINED`][]
            to not change.
        description
            The description to set for the command. Leave as [`hikari.undefined.UNDEFINED`][]
            to not change.
        options
            A sequence of up to 10 options to set for this command. Leave this as
            [`hikari.undefined.UNDEFINED`][] to not change.
        default_member_permissions
            Member permissions necessary to utilize this command by default.

            If `0`, then it will be available for all members. Note that this doesn't affect
            administrators of the guild and overwrites.

        Returns
        -------
        hikari.commands.PartialCommand
            The edited command object.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands.
        hikari.errors.NotFoundError
            If the provided application or command isn't found.
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_application_command(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        command: snowflakes.SnowflakeishOr[commands.PartialCommand],
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
    ) -> None:
        """Delete a registered application command.

        Parameters
        ----------
        application
            Object or ID of the application to delete a command for.
        command
            Object or ID of the command to delete.
        guild
            Object or ID of the guild to delete a command for if this is a guild
            specific command. Leave this as [`hikari.undefined.UNDEFINED`][] to
            delete a global command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands.
        hikari.errors.NotFoundError
            If the provided application or command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_application_guild_commands_permissions(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
    ) -> typing.Sequence[commands.GuildCommandPermissions]:
        """Fetch the command permissions registered in a guild.

        Parameters
        ----------
        application
            Object or ID of the application to fetch the command permissions for.
        guild
            Object or ID of the guild to fetch the command permissions for.

        Returns
        -------
        typing.Sequence[hikari.commands.GuildCommandPermissions]
            Sequence of the guild command permissions set for the specified guild.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands or guild.
        hikari.errors.NotFoundError
            If the provided application isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_application_command_permissions(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        command: snowflakes.SnowflakeishOr[commands.PartialCommand],
    ) -> commands.GuildCommandPermissions:
        """Fetch the permissions registered for a specific command in a guild.

        Parameters
        ----------
        application
            Object or ID of the application to fetch the command permissions for.
        guild
            Object or ID of the guild to fetch the command permissions for.
        command
            Object or ID of the command to fetch the command permissions for.

        Returns
        -------
        hikari.commands.GuildCommandPermissions
            Object of the command permissions set for the specified command.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands or guild.
        hikari.errors.NotFoundError
            If the provided application or command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    # THIS IS AN OAUTH2 FLOW ONLY
    @abc.abstractmethod
    async def set_application_command_permissions(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        command: snowflakes.SnowflakeishOr[commands.PartialCommand],
        permissions: typing.Sequence[commands.CommandPermission],
    ) -> commands.GuildCommandPermissions:
        """Set permissions for a specific command.

        !!! note
            This requires the `access_token` to have the
            [`hikari.applications.OAuth2Scope.APPLICATIONS_COMMANDS_PERMISSION_UPDATE`][]
            scope enabled along with the authorization of a Bot which has
            [`hikari.permissions.Permissions.CREATE_INSTANT_INVITE`][] permission
            within the target guild.

        !!! note
            This overwrites any previously set permissions.

        Parameters
        ----------
        application
            Object or ID of the application to set the command permissions for.
        guild
            Object or ID of the guild to set the command permissions for.
        command
            Object or ID of the command to set the permissions for.
        permissions
            Sequence of up to 10 of the permission objects to set.

        Returns
        -------
        hikari.commands.GuildCommandPermissions
            Object of the set permissions.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the provided application's commands or guild.
        hikari.errors.NotFoundError
            If the provided application or command isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def interaction_deferred_builder(
        self, type: base_interactions.ResponseType | int, /
    ) -> special_endpoints.InteractionDeferredBuilder:
        """Create a builder for a deferred message interaction response.

        Parameters
        ----------
        type
            The type of deferred message response this builder is for.

        Returns
        -------
        hikari.api.special_endpoints.InteractionDeferredBuilder
            The deferred message interaction response builder object.
        """

    @abc.abstractmethod
    def interaction_autocomplete_builder(
        self, choices: typing.Sequence[special_endpoints.AutocompleteChoiceBuilder]
    ) -> special_endpoints.InteractionAutocompleteBuilder:
        """Create a builder for an autocomplete interaction response.

        Parameters
        ----------
        choices
            The autocomplete choices.

        Returns
        -------
        hikari.api.special_endpoints.InteractionAutocompleteBuilder
            The autocomplete interaction response builder object.
        """

    @abc.abstractmethod
    def interaction_message_builder(
        self, type: base_interactions.ResponseType | int, /
    ) -> special_endpoints.InteractionMessageBuilder:
        """Create a builder for a message interaction response.

        Parameters
        ----------
        type
            The type of message response this builder is for.

        Returns
        -------
        hikari.api.special_endpoints.InteractionMessageBuilder
            The interaction message response builder object.
        """

    @abc.abstractmethod
    def interaction_modal_builder(self, title: str, custom_id: str) -> special_endpoints.InteractionModalBuilder:
        """Create a builder for a modal interaction response.

        Parameters
        ----------
        title
            The title that will show up in the modal.
        custom_id
            Developer set custom ID used for identifying interactions with this modal.

        Returns
        -------
        hikari.api.special_endpoints.InteractionModalBuilder
            The interaction modal response builder object.
        """

    @abc.abstractmethod
    async def fetch_interaction_response(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication], token: str
    ) -> messages_.Message:
        """Fetch the initial response for an interaction.

        Parameters
        ----------
        application
            Object or ID of the application to fetch a command for.
        token
            Token of the interaction to get the initial response for.

        Returns
        -------
        hikari.messages.Message
            Message object of the initial response.

        Raises
        ------
        hikari.errors.ForbiddenError
            If you cannot access the target interaction.
        hikari.errors.NotFoundError
            If the initial response isn't found.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_interaction_response(
        self,
        interaction: snowflakes.SnowflakeishOr[base_interactions.PartialInteraction],
        token: str,
        response_type: int | base_interactions.ResponseType,
        content: undefined.UndefinedOr[typing.Any] = undefined.UNDEFINED,
        *,
        flags: int | messages_.MessageFlag | undefined.UndefinedType = undefined.UNDEFINED,
        tts: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        attachment: undefined.UndefinedNoneOr[files.Resourceish] = undefined.UNDEFINED,
        attachments: undefined.UndefinedNoneOr[typing.Sequence[files.Resourceish]] = undefined.UNDEFINED,
        component: undefined.UndefinedNoneOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedNoneOr[
            typing.Sequence[special_endpoints.ComponentBuilder]
        ] = undefined.UNDEFINED,
        embed: undefined.UndefinedNoneOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedNoneOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        poll: undefined.UndefinedOr[special_endpoints.PollBuilder] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
    ) -> None:
        """Create the initial response for a interaction.

        !!! warning
            Calling this with an interaction which already has an initial
            response will result in this raising a [`hikari.errors.NotFoundError`][].
            This includes if the REST interaction server has already responded
            to the request.

        Parameters
        ----------
        interaction
            Object or ID of the interaction this response is for.
        token
            The interaction's token.
        response_type
            The type of interaction response this is.
        content
            If provided, the message contents. If
            [`hikari.undefined.UNDEFINED`][], then nothing will be sent
            in the content. Any other value here will be cast to a
            [`str`][].

            If this is a [`hikari.embeds.Embed`][] and no `embed` nor
            no `embeds` kwarg is provided, then this will instead
            update the embed. This allows for simpler syntax when
            sending an embed alone.
        attachment
            If provided, the message attachment. This can be a resource,
            or string of a path on your computer or a URL.
        attachments
            If provided, the message attachments. These can be resources, or
            strings consisting of paths on your computer or URLs.
        component
            If provided, builder object of the component to include in this message.
        components
            If provided, a sequence of the component builder objects to include
            in this message.
        embed
            If provided, the message embed.
        embeds
            If provided, the message embeds.
        poll
            If provided, the poll to add to the message.
        flags
            If provided, the message flags this response should have.

            As of writing the only message flags which can be set here are
            [`hikari.messages.MessageFlag.EPHEMERAL`][],
            [`hikari.messages.MessageFlag.SUPPRESS_NOTIFICATIONS`][]
            and [`hikari.messages.MessageFlag.SUPPRESS_EMBEDS`][].
        tts
            If provided, whether the message will be read out by a screen
            reader using Discord's TTS (text-to-speech) system.
        mentions_everyone
            If provided, whether the message should parse @everyone/@here
            mentions.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If provided, and [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If provided, and [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.

        Raises
        ------
        ValueError
            If more than 100 unique objects/entities are passed for
            `role_mentions` or `user_mentions`.
        TypeError
            If both `embed` and `embeds` are specified.
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no embeds; messages with more than 2000 characters
            in them, embeds that exceed one of the many embed limits
            invalid image URLs in embeds.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction is not found or if the interaction's initial
            response has already been created.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_interaction_voice_message_response(
        self,
        interaction: snowflakes.SnowflakeishOr[base_interactions.PartialInteraction],
        token: str,
        attachment: files.Resourceish,
        waveform: str,
        duration: float,
        *,
        flags: int | messages_.MessageFlag | undefined.UndefinedType = undefined.UNDEFINED,
    ) -> None:
        """Create the a initial voice message response for a interaction.

        !!! warning
            Calling this with an interaction which already has an initial
            response will result in this raising a [`hikari.errors.NotFoundError`][].
            This includes if the REST interaction server has already responded
            to the request.

        Parameters
        ----------
        interaction
            Object or ID of the interaction this response is for.
        token
            The interaction's token.
        attachment
            The audio attachment used as source for the voice message.
            This can be a resource, or string of a path on your computer
            or a URL. The Content-Type of the attachment has to start with
            `audio/`.
        waveform
            The waveform of the entire voice message, with 1 byte
            per datapoint encoded in base64.

            Official clients sample the recording at most once per 100
            milliseconds, but will downsample so that no more than 256
            datapoints are in the waveform.

            !!! note
                Discord states that this is implementation detail and might
                change without notice. You have been warned!
        duration
            The duration of the voice message in seconds. This is intended to be
            a float.
        flags
            If provided, the message flags this response should have.

            As of writing the only message flags which can be set here are
            [`hikari.messages.MessageFlag.EPHEMERAL`][],
            [`hikari.messages.MessageFlag.SUPPRESS_NOTIFICATIONS`][]
            and [`hikari.messages.MessageFlag.SUPPRESS_EMBEDS`][].

        Raises
        ------
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no embeds; messages with more than 2000 characters
            in them, embeds that exceed one of the many embed limits
            invalid image URLs in embeds.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction is not found or if the interaction's initial
            response has already been created.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_interaction_response(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        token: str,
        content: undefined.UndefinedNoneOr[typing.Any] = undefined.UNDEFINED,
        *,
        attachment: undefined.UndefinedNoneOr[files.Resourceish | messages_.Attachment] = undefined.UNDEFINED,
        attachments: undefined.UndefinedNoneOr[
            typing.Sequence[files.Resourceish | messages_.Attachment]
        ] = undefined.UNDEFINED,
        component: undefined.UndefinedNoneOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedNoneOr[
            typing.Sequence[special_endpoints.ComponentBuilder]
        ] = undefined.UNDEFINED,
        embed: undefined.UndefinedNoneOr[embeds_.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedNoneOr[typing.Sequence[embeds_.Embed]] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[users.PartialUser] | bool
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[guilds.PartialRole] | bool
        ] = undefined.UNDEFINED,
    ) -> messages_.Message:
        """Edit the initial response to a command interaction.

        !!! note
            Mentioning everyone, roles, or users in message edits currently
            will not send a push notification showing a new mention to people
            on Discord. It will still highlight in their chat as if they
            were mentioned, however.

            Also important to note that if you specify a text `content`, `mentions_everyone`,
            `mentions_reply`, `user_mentions`, and `role_mentions` will default
            to [`False`][] as the message will be re-parsed for mentions. This will
            also occur if only one of the four are specified

            This is a limitation of Discord's design. If in doubt, specify all
            four of them each time.

        Parameters
        ----------
        application
            Object or ID of the application to edit a command response for.
        token
            The interaction's token.
        content
            If provided, the message content to update with. If
            [`hikari.undefined.UNDEFINED`][], then the content will not
            be changed. If [`None`][], then the content will be removed.

            Any other value will be cast to a [`str`][] before sending.

            If this is a [`hikari.embeds.Embed`][] and neither the
            `embed` or `embeds` kwargs are provided or if this is a
            [`hikari.files.Resourceish`][] and neither the `attachment` or
            `attachments` kwargs are provided, the values will be overwritten.
            This allows for simpler syntax when sending an embed or an
            attachment alone.
        attachment
            If provided, the attachment to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous attachment, if
            present, is not changed. If this is [`None`][], then the
            attachment is removed, if present. Otherwise, the new attachment
            that was provided will be attached.
        attachments
            If provided, the attachments to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous attachments, if
            present, are not changed. If this is [`None`][], then the
            attachments is removed, if present. Otherwise, the new attachments
            that were provided will be attached.
        component
            If provided, builder object of the component to set for this message.
            This component will replace any previously set components and passing
            [`None`][] will remove all components.
        components
            If provided, a sequence of the component builder objects set for
            this message. These components will replace any previously set
            components and passing [`None`][] or an empty sequence will
            remove all components.
        embed
            If provided, the embed to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous embed(s) are not changed.
            If this is [`None`][] then any present embeds are removed.
            Otherwise, the new embed that was provided will be used as the
            replacement.
        embeds
            If provided, the embeds to set on the message. If
            [`hikari.undefined.UNDEFINED`][], the previous embed(s) are not changed.
            If this is [`None`][] then any present embeds are removed.
            Otherwise, the new embeds that were provided will be used as the
            replacement.
        mentions_everyone
            If provided, whether the message should parse @everyone/@here
            mentions.
        user_mentions
            If provided, and [`True`][], all user mentions will be detected.
            If provided, and [`False`][], all user mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.users.PartialUser`][] derivatives to enforce mentioning
            specific users.
        role_mentions
            If provided, and [`True`][], all role mentions will be detected.
            If provided, and [`False`][], all role mentions will be ignored
            if appearing in the message body.
            Alternatively this may be a collection of
            [`hikari.snowflakes.Snowflake`][], or
            [`hikari.guilds.PartialRole`][] derivatives to enforce mentioning
            specific roles.

        Returns
        -------
        hikari.messages.Message
            The edited message.

        Raises
        ------
        ValueError
            If both `attachment` and `attachments`, `component` and `components`
            or `embed` and `embeds` are specified.
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction or the message are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_interaction_voice_message_response(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        token: str,
        attachment: files.Resourceish | messages_.Attachment,
        waveform: str,
        duration: float,
    ) -> messages_.Message:
        """Edit the initial response to a voice message.

        !!! note
            Even though this edits the initial response, this only works for
            editing/responding to deferred responses. Voice messages can not
            be edited.

        Parameters
        ----------
        application
            Object or ID of the application to edit a command response for.
        token
            The interaction's token.
        attachment
            The audio attachment used as source for the voice message.
            This can be a resource, or string of a path on your computer
            or a URL. The Content-Type of the attachment has to start with
            `audio/`.
        waveform
            The waveform of the entire voice message, with 1 byte
            per datapoint encoded in base64.

            Official clients sample the recording at most once per 100
            milliseconds, but will downsample so that no more than 256
            datapoints are in the waveform.

            !!! note
                Discord states that this is implementation detail and might
                change without notice. You have been warned!
        duration
            The duration of the voice message in seconds. This is intended to be
            a float.


        Returns
        -------
        hikari.messages.Message
            The edited message.

        Raises
        ------
        hikari.errors.BadRequestError
            This may be raised in several discrete situations, such as messages
            being empty with no attachments or embeds; messages with more than
            2000 characters in them, embeds that exceed one of the many embed
            limits; too many attachments; attachments that are too large;
            invalid image URLs in embeds; too many components.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction or the message are not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_interaction_response(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication], token: str
    ) -> None:
        """Delete the initial response of an interaction.

        Parameters
        ----------
        application
            Object or ID of the application to delete a command response for.
        token
            The interaction's token.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction or response is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_autocomplete_response(
        self,
        interaction: snowflakes.SnowflakeishOr[base_interactions.PartialInteraction],
        token: str,
        choices: typing.Sequence[special_endpoints.AutocompleteChoiceBuilder],
    ) -> None:
        """Create the initial response for an autocomplete interaction.

        Parameters
        ----------
        interaction
            Object or ID of the interaction this response is for.
        token
            The interaction's token.
        choices
            The autocomplete choices themselves.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction is not found or if the interaction's initial
            response has already been created.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_modal_response(
        self,
        interaction: snowflakes.SnowflakeishOr[base_interactions.PartialInteraction],
        token: str,
        *,
        title: str,
        custom_id: str,
        component: undefined.UndefinedOr[special_endpoints.ComponentBuilder] = undefined.UNDEFINED,
        components: undefined.UndefinedOr[typing.Sequence[special_endpoints.ComponentBuilder]] = undefined.UNDEFINED,
    ) -> None:
        """Create a response by sending a modal.

        Parameters
        ----------
        interaction
            Object or ID of the interaction this response is for.
        token
            The interaction's token.
        title
            The title that will show up in the modal.
        custom_id
            Developer set custom ID used for identifying interactions with this modal.
        component
            A component builders to send in this modal.
        components
            A sequence of component builders to send in this modal.

        Raises
        ------
        ValueError
            If both `component` and `components` are specified or if none are specified.
        """

    @abc.abstractmethod
    def build_message_action_row(self) -> special_endpoints.MessageActionRowBuilder:
        """Build a message action row message component for use in message create and REST calls.

        Returns
        -------
        hikari.api.special_endpoints.MessageActionRowBuilder
            The initialised action row builder.
        """

    @abc.abstractmethod
    def build_modal_action_row(self) -> special_endpoints.ModalActionRowBuilder:
        """Build an action row modal component for use in interactions and REST calls.

        Returns
        -------
        hikari.api.special_endpoints.ModalActionRowBuilder
            The initialised action row builder.
        """

    @abc.abstractmethod
    async def fetch_scheduled_event(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        event: snowflakes.SnowflakeishOr[scheduled_events.ScheduledEvent],
        /,
    ) -> scheduled_events.ScheduledEvent:
        """Fetch a scheduled event.

        Parameters
        ----------
        guild
            The guild the event bellongs to. This may be the object or the
            ID of an existing guild.
        event
            The event to fetch. This may be the object or the
            ID of an existing event.

        Returns
        -------
        hikari.scheduled_events.ScheduledEvent
            The scheduled event.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the permission needed to view this event.

            For `VOICE` and `STAGE_CHANNEL` events, [`hikari.permissions.Permissions.VIEW_CHANNEL`][]
            is required in their associated guild to see the event.
        hikari.errors.NotFoundError
            If the guild or event is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_scheduled_events(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], /
    ) -> typing.Sequence[scheduled_events.ScheduledEvent]:
        """Fetch the scheduled events for a guild.

        !!! note
            `VOICE` and `STAGE_CHANNEL` events are only included if the bot has
            `VOICE` or `STAGE_CHANNEL` permissions in the associated channel.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch scheduled events for.

        Returns
        -------
        typing.Sequence[hikari.scheduled_events.ScheduledEvent]
            Sequence of the scheduled events.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_stage_event(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        channel: snowflakes.SnowflakeishOr[channels_.PartialChannel],
        name: str,
        /,
        start_time: datetime.datetime,
        *,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        end_time: undefined.UndefinedOr[datetime.datetime] = undefined.UNDEFINED,
        image: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        privacy_level: int | scheduled_events.EventPrivacyLevel = scheduled_events.EventPrivacyLevel.GUILD_ONLY,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> scheduled_events.ScheduledStageEvent:
        """Create a scheduled stage event.

        Parameters
        ----------
        guild
            The guild to create the event in.
        channel
            The stage channel to create the event in.
        name
            The name of the event.
        start_time
            When the event is scheduled to start.
        description
            The event's description.
        end_time
            When the event should be scheduled to end.
        image
            The event's display image.
        privacy_level
            The event's privacy level.

            This effects who can view and subscribe to the event.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.scheduled_events.ScheduledStageEvent
            The created scheduled stage event.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing permissions to create the scheduled event.

            You need the following permissions in the target stage channel:
            [`hikari.permissions.Permissions.MANAGE_EVENTS`][],
            [`hikari.permissions.Permissions.VIEW_CHANNEL`][],
            and [`hikari.permissions.Permissions.CONNECT`][].
        hikari.errors.NotFoundError
            If the guild or event is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_voice_event(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        channel: snowflakes.SnowflakeishOr[channels_.PartialChannel],
        name: str,
        /,
        start_time: datetime.datetime,
        *,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        end_time: undefined.UndefinedOr[datetime.datetime] = undefined.UNDEFINED,
        image: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        privacy_level: int | scheduled_events.EventPrivacyLevel = scheduled_events.EventPrivacyLevel.GUILD_ONLY,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> scheduled_events.ScheduledVoiceEvent:
        """Create a scheduled voice event.

        Parameters
        ----------
        guild
            The guild to create the event in.
        channel
            The voice channel to create the event in.
        name
            The name of the event.
        start_time
            When the event is scheduled to start.
        description
            The event's description.
        end_time
            When the event should be scheduled to end.
        image
            The event's display image.
        privacy_level
            The event's privacy level.

            This effects who can view and subscribe to the event.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.scheduled_events.ScheduledVoiceEvent
            The created scheduled voice event.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing permissions to create the scheduled event.

            You need the following permissions in the target voice channel:
            [`hikari.permissions.Permissions.MANAGE_EVENTS`][],
            [`hikari.permissions.Permissions.VIEW_CHANNEL`][],
            and [`hikari.permissions.Permissions.CONNECT`][].
        hikari.errors.NotFoundError
            If the guild or event is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_external_event(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        name: str,
        /,
        location: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        *,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        image: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        privacy_level: int | scheduled_events.EventPrivacyLevel = scheduled_events.EventPrivacyLevel.GUILD_ONLY,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> scheduled_events.ScheduledExternalEvent:
        """Create a scheduled external event.

        Parameters
        ----------
        guild
            The guild to create the event in.
        name
            The name of the event.
        location
            The location the event.
        start_time
            When the event is scheduled to start.
        end_time
            When the event is scheduled to end.
        description
            The event's description.
        image
            The event's display image.
        privacy_level
            The event's privacy level.

            This effects who can view and subscribe to the event.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.scheduled_events.ScheduledExternalEvent
            The created scheduled external event.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_EVENTS`][] permission.
        hikari.errors.NotFoundError
            If the guild or event is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_scheduled_event(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        event: snowflakes.SnowflakeishOr[scheduled_events.ScheduledEvent],
        /,
        *,
        channel: undefined.UndefinedNoneOr[snowflakes.SnowflakeishOr[channels_.PartialChannel]] = undefined.UNDEFINED,
        description: undefined.UndefinedNoneOr[str] = undefined.UNDEFINED,
        entity_type: undefined.UndefinedOr[int | scheduled_events.ScheduledEventType] = undefined.UNDEFINED,
        image: undefined.UndefinedOr[files.Resourceish] = undefined.UNDEFINED,
        location: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        privacy_level: undefined.UndefinedOr[int | scheduled_events.EventPrivacyLevel] = undefined.UNDEFINED,
        start_time: undefined.UndefinedOr[datetime.datetime] = undefined.UNDEFINED,
        end_time: undefined.UndefinedNoneOr[datetime.datetime] = undefined.UNDEFINED,
        status: undefined.UndefinedOr[int | scheduled_events.ScheduledEventStatus] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> scheduled_events.ScheduledEvent:
        """Edit a scheduled event.

        Parameters
        ----------
        guild
            The guild to edit the event in.
        event
            The scheduled event to edit.
        channel
            The channel a `VOICE` or `STAGE` event should be associated with.
        description
            The event's description.
        entity_type
            The type of entity the event should target.
        image
            The event's display image.
        location
            The location of an `EXTERNAL` event.

            Must be passed when changing an event to `EXTERNAL`.
        name
            The event's name.
        privacy_level
            The event's privacy level.

            This effects who can view and subscribe to the event.
        start_time
            When the event should be scheduled to start.
        end_time
            When the event should be scheduled to end.

            This can only be set to [`None`][] for `STAGE` and `VOICE` events.
            Must be provided when changing an event to `EXTERNAL`.
        status
            The event's new status.

            `SCHEDULED` events can be set to `ACTIVE` and `CANCELED`.
            `ACTIVE` events can only be set to `COMPLETED`.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.scheduled_events.ScheduledEvent
            The edited scheduled event.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing permissions to edit the scheduled event.

            For `VOICE` and `STAGE_INSTANCE` events, you need the following
            permissions in the event's associated channel: [`hikari.permissions.Permissions.MANAGE_EVENTS`][],
            [`hikari.permissions.Permissions.VIEW_CHANNEL`][] and [`hikari.permissions.Permissions.CONNECT`][].

            For `EXTERNAL` events you just need the [`hikari.permissions.Permissions.MANAGE_EVENTS`][] permission.
        hikari.errors.NotFoundError
            If the guild or event is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_scheduled_event(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        event: snowflakes.SnowflakeishOr[scheduled_events.ScheduledEvent],
        /,
    ) -> None:
        """Delete a scheduled event.

        Parameters
        ----------
        guild
            The guild to delete the event from.
        event
            The scheduled event to delete.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are missing the [`hikari.permissions.Permissions.MANAGE_EVENTS`][] permission.
        hikari.errors.NotFoundError
            If the guild or event is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def fetch_scheduled_event_users(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        event: snowflakes.SnowflakeishOr[scheduled_events.ScheduledEvent],
        /,
        *,
        newest_first: bool = False,
        start_at: undefined.UndefinedOr[snowflakes.SearchableSnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
    ) -> iterators.LazyIterator[scheduled_events.ScheduledEventUser]:
        """Asynchronously iterate over the users who're subscribed to a scheduled event.

        !!! note
            This call is not a coroutine function, it returns a special type of
            lazy iterator that will perform API calls as you iterate across it,
            thus any errors documented below will happen then.

            See [`hikari.iterators`][] for the full API for this iterator type.

        Parameters
        ----------
        guild
            The guild to fetch the scheduled event users from.
        event
            The scheduled event to fetch the subscribed users for.
        newest_first
            Whether to fetch the newest first or the oldest first.
        start_at
            If provided, will start at this snowflake. If you provide
            a datetime object, it will be transformed into a snowflake. This
            may also be a scheduled event object object. In this case, the
            date the object was first created will be used.

        Returns
        -------
        hikari.iterators.LazyIterator[hikari.scheduled_events.ScheduledEventUser]
            The token's associated guilds.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or event was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_skus(
        self, application: snowflakes.SnowflakeishOr[guilds.PartialApplication]
    ) -> typing.Sequence[monetization.SKU]:
        """Fetch all SKUs for a given application.

        Because of how Discord's SKU and subscription systems work,
        you will see two SKUs for your premium offering.

        For integration and testing entitlements, you should use the SKU with type:
        `hikari.monetization.SKUType.SUBSCRIPTION`.

        Parameters
        ----------
        application
            The application to fetch SKUs for.

        Returns
        -------
        typing.Sequence[hikari.monetization.SKU]
            The SKUs for the application.

        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_entitlements(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        /,
        *,
        user: undefined.UndefinedOr[snowflakes.SnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
        guild: undefined.UndefinedOr[snowflakes.SnowflakeishOr[guilds.PartialGuild]] = undefined.UNDEFINED,
        before: undefined.UndefinedOr[snowflakes.SearchableSnowflakeish] = undefined.UNDEFINED,
        after: undefined.UndefinedOr[snowflakes.SearchableSnowflakeish] = undefined.UNDEFINED,
        limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        exclude_ended: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> typing.Sequence[monetization.Entitlement]:
        """Fetch all entitlements for a given application, active and expired.

        Parameters
        ----------
        application
            The application to fetch entitlements for.
        user
            The user to look up entitlements for.
        guild
            The guild to look up entitlements for.
        before
            Retrieve entitlements before this time or ID.
        after
            Retrieve entitlements after this time or ID.
        limit
            Number of entitlements to return, 1-100, default 100.
        exclude_ended
            Whether or not ended entitlements should be omitted.

        Returns
        -------
        typing.Sequence[hikari.entitlements.Entitlement]
            The entitlements for the application that match the criteria.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or user was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_test_entitlement(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        /,
        *,
        sku: snowflakes.SnowflakeishOr[monetization.SKU],
        owner_id: snowflakes.Snowflakeish,
        owner_type: monetization.EntitlementOwnerType,
    ) -> monetization.Entitlement:
        """Create a test entitlement for a given SKU.

        .. note::
            The created entitlement is only partial and the `subscription_id`,
            `starts_at` and `ends_at` fields will be [`None`][].

        Parameters
        ----------
        application
            The application to create the entitlement for.
        sku
            The SKU to create a test entitlement for.
        owner_id
            The ID of the owner of the entitlement.
        owner_type
            The type of the owner of the entitlement.

        Returns
        -------
        hikari.entitlements.Entitlement
            The created partial entitlement.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the SKU or owner was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_test_entitlement(
        self,
        application: snowflakes.SnowflakeishOr[guilds.PartialApplication],
        entitlement: snowflakes.SnowflakeishOr[monetization.Entitlement],
        /,
    ) -> None:
        """Delete a test entitlement.

        Parameters
        ----------
        application
            The application to delete the entitlement from.
        entitlement
            The entitlement to delete.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the entitlement was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_stage_instance(
        self, channel: snowflakes.SnowflakeishOr[channels_.GuildStageChannel]
    ) -> stage_instances.StageInstance:
        """Fetch the stage instance associated with a guild stage channel.

        Parameters
        ----------
        channel
            The guild stage channel to fetch the stage instance from.

        Returns
        -------
        hikari.stage_instances.StageInstance
            The stage instance associated with the guild stage channel.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the stage instance or channel is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_stage_instance(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildStageChannel],
        *,
        topic: str,
        privacy_level: undefined.UndefinedOr[int | stage_instances.StageInstancePrivacyLevel],
        send_start_notification: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        scheduled_event_id: undefined.UndefinedOr[
            snowflakes.SnowflakeishOr[scheduled_events.ScheduledEvent]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> stage_instances.StageInstance:
        """Create a stage instance in guild stage channel.

        Parameters
        ----------
        channel
            The channel to use for the stage instance creation.
        topic
            The topic for the stage instance.
        privacy_level
            The privacy level for the stage instance.
        send_start_notification
            Whether to send a notification to *all* server members that the stage instance has started.
        scheduled_event_id
            The ID of the scheduled event to associate with the stage instance.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.stage_instances.StageInstance
            The created stage instance.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction or response is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_stage_instance(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildStageChannel],
        *,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        privacy_level: undefined.UndefinedOr[int | stage_instances.StageInstancePrivacyLevel] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> stage_instances.StageInstance:
        """Edit the stage instance in a guild stage channel.

        Parameters
        ----------
        channel
            The channel that the stage instance is associated with.
        topic
            The topic for the stage instance.
        privacy_level
            The privacy level for the stage instance.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.stage_instances.StageInstance
            The edited stage instance.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token
            or you are not a moderator of the stage instance).
        hikari.errors.NotFoundError
            If the interaction or response is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_stage_instance(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.GuildStageChannel],
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete the stage instance.

        Parameters
        ----------
        channel
            The guild stage channel to fetch the stage instance from.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the interaction or response is not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.RateLimitedError
            Usually, Hikari will handle and retry on hitting
            rate-limits automatically. This includes most bucket-specific
            rate-limits and global rate-limits. In some rare edge cases,
            however, Discord implements other undocumented rules for
            rate-limiting, such as limits per attribute. These cannot be
            detected or handled normally by Hikari due to their undocumented
            nature, and will trigger this exception if they occur.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_poll_voters(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        answer_id: int,
        /,
        *,
        after: undefined.UndefinedOr[snowflakes.SnowflakeishOr[users.PartialUser]] = undefined.UNDEFINED,
        limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> typing.Sequence[users.User]:
        """Fetch users that voted for a specific answer.

        Parameters
        ----------
        channel
            The channel the poll is in.
        message
            The message the poll is in.
        answer_id
            The answers id.
        after
            The votes to collect, after this user voted.
        limit
            The amount of votes to collect. Maximum 100, default 25

        Returns
        -------
        typing.Sequence[users.User]
            An sequence of Users.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the entitlement was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def end_poll(
        self,
        channel: snowflakes.SnowflakeishOr[channels_.TextableChannel],
        message: snowflakes.SnowflakeishOr[messages_.PartialMessage],
        /,
    ) -> messages_.Message:
        """End a poll.

        Parameters
        ----------
        channel
            The channel the poll is in.
        message
            The message the poll is in.

        Returns
        -------
        hikari.messages.Message
            The message that had its poll ended.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the entitlement was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_auto_mod_rules(
        self, guild: snowflakes.SnowflakeishOr[guilds.PartialGuild], /
    ) -> typing.Sequence[auto_mod.AutoModRule]:
        """Fetch a guild's auto-moderation rules.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch the auto-moderation rules of.

        Returns
        -------
        typing.Sequence[hikari.auto_mod.AutoModRule]
            Sequence of the guild's auto-moderation rules.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the `MANAGE_GUILD` permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def fetch_auto_mod_rule(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        rule: snowflakes.SnowflakeishOr[auto_mod.AutoModRule],
        /,
    ) -> auto_mod.AutoModRule:
        """Fetch an auto-moderation rule.

        Parameters
        ----------
        guild
            Object or ID of the guild to fetch the auto-moderation rules of.
        rule
            Object or ID of the auto-moderation rule to fetch.

        Returns
        -------
        hikari.auto_mod.AutoModRule
            The fetched auto-moderation rule.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the `MANAGE_GUILD` permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or rule was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def create_auto_mod_rule(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        *,
        name: str,
        event_type: auto_mod.AutoModEventType | int,
        trigger: special_endpoints.AutoModTriggerBuilder,
        actions: typing.Sequence[special_endpoints.AutoModActionBuilder],
        enabled: undefined.UndefinedOr[bool] = True,
        exempt_roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        exempt_channels: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[channels_.PartialChannel]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> auto_mod.AutoModRule:
        """Create an auto-moderation rule.

        Parameters
        ----------
        guild
            Object or ID of the guild to create the auto-moderation rules in.
        name
            The rule's name.
        event_type
            The type of user content creation event this rule should trigger on.
        trigger
            The trigger builder to create the rule from.
        actions
            Sequence of the actions to execute when this rule is triggered.
        enabled
            Whether this auto-moderation rule should be enabled.
        exempt_channels
            Sequence of up to 50 objects and IDs of channels which are not
            effected by the rule.
        exempt_roles
            Sequence of up to 20 objects and IDs of roles which are not
            effected by the rule.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.auto_mod.AutoModRule
            The created auto-moderation rule.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the `MANAGE_GUILD` permission or if you try to
            set a TIMEOUT action without the `MODERATE_MEMBERS` permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def edit_auto_mod_rule(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        rule: snowflakes.SnowflakeishOr[auto_mod.AutoModRule],
        *,
        name: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        event_type: undefined.UndefinedOr[auto_mod.AutoModEventType | int] = undefined.UNDEFINED,
        trigger: undefined.UndefinedOr[special_endpoints.AutoModTriggerBuilder] = undefined.UNDEFINED,
        actions: undefined.UndefinedOr[typing.Sequence[special_endpoints.AutoModActionBuilder]] = undefined.UNDEFINED,
        enabled: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        exempt_roles: undefined.UndefinedOr[snowflakes.SnowflakeishSequence[guilds.PartialRole]] = undefined.UNDEFINED,
        exempt_channels: undefined.UndefinedOr[
            snowflakes.SnowflakeishSequence[channels_.PartialChannel]
        ] = undefined.UNDEFINED,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> auto_mod.AutoModRule:
        """Edit an auto-moderation rule.

        Parameters
        ----------
        guild
            Object or ID of the guild to edit an auto-moderation rule in.
        rule
            Object or ID of the auto-moderation rule to edit.
        name
            If specified, the rule's new name.
        event_type
            The type of user content creation event this rule should trigger on.
        trigger
            The trigger builder to edit the trigger from.
        actions
            If specified, a sequence of the actions to execute when this rule
            is triggered.
        enabled
            If specified, whether this auto-moderation rule should be enabled.
        exempt_channels
            If specified, a sequence of up to 50 objects and IDs of channels
            which are not effected by the rule.
        exempt_roles
            If specified, a sequence of up to 20 objects and IDs of roles which
            are not effected by the rule.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.auto_mod.AutoModRule
            The created auto-moderation rule.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the `MANAGE_GUILD` permission or if you try to
            set a TIMEOUT action without the `MODERATE_MEMBERS` permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    async def delete_auto_mod_rule(
        self,
        guild: snowflakes.SnowflakeishOr[guilds.PartialGuild],
        rule: snowflakes.SnowflakeishOr[auto_mod.AutoModRule],
        *,
        reason: undefined.UndefinedOr[str] = undefined.UNDEFINED,
    ) -> None:
        """Delete an auto-moderation rule.

        Parameters
        ----------
        guild
            Object or ID of the guild to delete the auto-moderation rules of.
        rule
            Object or ID of the auto-moderation rule to delete.
        reason
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Raises
        ------
        hikari.errors.BadRequestError
            If any of the fields that are passed have an invalid value.
        hikari.errors.ForbiddenError
            If you are missing the `MANAGE_GUILD` permission.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.NotFoundError
            If the guild or rule was not found.
        hikari.errors.RateLimitTooLongError
            Raised in the event that a rate limit occurs that is
            longer than `max_rate_limit` when making a request.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """
