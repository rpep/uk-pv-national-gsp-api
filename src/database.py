""" Functions to read from the database and format """
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List

from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models import Forecast, GSPYield, ManyForecasts
from nowcasting_datamodel.read.read import (
    get_all_gsp_ids_latest_forecast,
    get_latest_forecast,
    get_latest_national_forecast,
)
from nowcasting_datamodel.read.read_gsp import get_gsp_yield
from sqlalchemy.orm.session import Session

logger = logging.getLogger(__name__)


def get_forecasts_from_database(session: Session) -> ManyForecasts:
    """Get forecasts from database for all GSPs"""
    # sql sqlalchemy objects
    forecasts = get_all_gsp_ids_latest_forecast(session=session)

    # change to pydantic objects
    forecasts = [Forecast.from_orm(forecast) for forecast in forecasts]

    # return as many forecasts
    return ManyForecasts(forecasts=forecasts)


def get_forecasts_for_a_specific_gsp_from_database(session: Session, gsp_id) -> Forecast:
    """Get forecasts for on GSP from database"""
    # get forecast from database
    forecast = get_latest_forecast(session=session, gsp_id=gsp_id)

    return Forecast.from_orm(forecast)


def get_session():
    """Get database settion"""
    connection = DatabaseConnection(url=os.getenv("DB_URL", "not_set"))

    with connection.get_session() as s:
        yield s


def get_session_pv():
    """Get database sessions to pv database"""
    connection = DatabaseConnection(url=os.getenv("DB_URL_PV", "not_set"))

    with connection.get_session() as s:
        yield s


def get_latest_national_forecast_from_database(session: Session) -> Forecast:
    """Get the national level forecast from the database"""

    logger.debug("Getting latest national forecast")

    forecast = get_latest_national_forecast(session=session)
    logger.debug(forecast)
    return Forecast.from_orm(forecast)


def get_truth_values_for_a_specific_gsp_from_database(
    session: Session, gsp_id: int, regime: str = "in-day"
) -> List[GSPYield]:
    """
    Get the truth value for one gsp for yesterday and today

    :param session: sql session
    :param gsp_id: gsp id
    :param regime: option for "in-day" or "day-after"
    :return: list of gsp yields
    """

    yesterday_start_datetime = datetime.now(tz=timezone.utc).date() - timedelta(days=1)
    yesterday_start_datetime = datetime.combine(yesterday_start_datetime, datetime.min.time())

    return get_gsp_yield(
        session=session,
        gsp_ids=[gsp_id],
        start_datetime_utc=yesterday_start_datetime,
        regime=regime,
    )
