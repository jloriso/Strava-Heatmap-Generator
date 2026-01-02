from dataClasses.ActivityRoute import ActivityRoute
import dbManager
import heatmapController
import environmentManager
import stravaRepository

if __name__ == "__main__":
    environmentManager.init_env()

    # activities = stravaRepository.get_newest_activites()

    # if activities:
    #     dbManager.save_activities_to_db([{
    #         "athleteid": activity.get("athlete", {}).get("id"),
    #         "activityid": activity.get("id"),
    #         "name": activity.get("name"),
    #         "start_date": activity.get("start_date"),
    #         "time_zone": activity.get("time_zone"),
    #         "activity_type": activity.get("sport_type"),
    #         "distance": activity.get("distance"),
    #         "moving_time": activity.get("moving_time"),
    #         "polyline": activity.get("map", {}).get("summary_polyline")
    #     } for activity in activities])

    dbModel = dbManager.load_activities_from_db()

    routes = ActivityRoute.build_many_from_db(dbModel)

    locations = {
        "USA": [38.0, -94.8, 5],
        "Chicago": [42.0707, -87.7368, 10],
        "Kalamazoo": [42.2, -85.6, 11],
        "World": [20.0, 0.0, 3]
    }

    heatmapController.build_activity_map(routes, locations=locations)