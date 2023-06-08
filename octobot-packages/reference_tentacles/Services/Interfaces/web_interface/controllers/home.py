#  Drakkar-Software OctoBot-Interfaces
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

import flask

import octobot_commons.authentication as authentication
import octobot_services.interfaces.util as interfaces_util
import tentacles.Services.Interfaces.web_interface as web_interface
import tentacles.Services.Interfaces.web_interface.login as login
import tentacles.Services.Interfaces.web_interface.models as models
import tentacles.Services.Interfaces.web_interface.flask_util as flask_util
import octobot.constants as constants
import tentacles.Services.Interfaces.octo_ui2.models.octo_ui2 as octo_ui2


def new_home():
    return flask.redirect("/octo_ui2/home")


octo_ui2.create_env_dependent_route(
    plugin=web_interface.server_instance,
    route="/",
    route_method=new_home,
    can_be_shared=True,
)


@web_interface.server_instance.route("/home")
@login.login_required_when_activated
def home():
    if flask.request.args.get("reset_tutorials", "False") == "True":
        flask_util.BrowsingDataProvider.instance().set_first_displays(True)
    if models.accepted_terms():
        in_backtesting = models.get_in_backtesting_mode()
        display_intro = flask_util.BrowsingDataProvider.instance().get_and_unset_is_first_display(
            flask_util.BrowsingDataProvider.HOME
        )
        form_to_display = constants.WELCOME_FEEDBACK_FORM_ID
        pnl_symbols = models.get_pnl_history_symbols()
        all_time_frames = models.get_all_watched_time_frames()
        display_time_frame = models.get_display_timeframe()
        display_orders = models.get_display_orders()
        try:
            user_id = models.get_user_account_id()
            display_feedback_form = form_to_display and not models.has_filled_form(form_to_display)
        except authentication.AuthenticationRequired:
            # no authenticated user: don't display form
            user_id = None
            display_feedback_form = False
        return flask.render_template(
            'index.html',
            has_pnl_history=bool(pnl_symbols),
            watched_symbols=models.get_watched_symbols(),
            backtesting_mode=in_backtesting,
            display_intro=display_intro,
            selected_profile=models.get_current_profile().name,
            reference_unit=interfaces_util.get_reference_market(),
            display_time_frame=display_time_frame,
            display_orders=display_orders,
            all_time_frames=all_time_frames,
            user_id=user_id,
            form_to_display=form_to_display,
            display_feedback_form=display_feedback_form,
        )
    else:
        return flask.redirect(flask.url_for("terms"))