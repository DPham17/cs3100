package rsck.chalkboard;

import android.os.Parcel;
import android.os.Parcelable;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.lang.reflect.Array;
import java.util.ArrayList;

/**
 * Created by Jacob.
 */
public class WeightedGrades implements Parcelable{
    private int ID;
    private String name;
    private double weight;
    private ArrayList<Assignment> assignments;

    public WeightedGrades(){assignments = new ArrayList<>();}

    public WeightedGrades(int cat_ID, int user_ID, String token){
        assignments = new ArrayList<Assignment>();
        ID = cat_ID;

        /*
        * Calls: http://cs3100.brod.es:3100/get/category/?token='token'&user='ID'
        * Where: {"id":ID}
        */
        DjangoFunctions django = new DjangoFunctions();
        JSONObject query = new JSONObject();

        try {
            query.put("id", ID);

            JSONObject response = django.access("category", Integer.toString(user_ID), token, query);
            JSONObject category = response.getJSONArray("data").getJSONObject(0);

            weight = category.getDouble("weight");
            name = category.getString("name");
        } catch (JSONException e) {
            e.printStackTrace();
        }

        loadAssignments(user_ID, token);
    }

    public void setWeight(double newWeight){weight = newWeight;}

    public double weightedTotal(){
        return weight * unweightedTotal();
    }

    public float unweightedTotal(){
        return pointsReceived() / pointsPossible();
    }

    public float pointsPossible(){
        float total = 0;

        for(Assignment assignment : assignments)
            total += assignment.pointsPossible;

        return total;
    }

    public float pointsReceived(){
        float total = 0;

        for(Assignment assignment : assignments)
            total += assignment.pointsReceived;

        return total;
    }

    public void loadAssignments(int user_ID, String token){
        DjangoFunctions django = new DjangoFunctions();

        /*
        * Calls: http://cs3100.brod.es:3100/get/homework/?token='token'&user='ID'
        * Where: {"category_id": 'ID'}
        */
        JSONObject query = new JSONObject();

        try {
            query.put("category_id", ID);

            JSONObject hwResponse = django.access("homework", Integer.toString(user_ID), token, query);
            JSONArray homeworks = hwResponse.getJSONArray("data");

            for(int i = 0; i < homeworks.length(); i++){
                JSONObject assignment = homeworks.getJSONObject(i);

                //TODO: Add to Assignments.
                Assignment newAssignment = new Assignment(assignment, user_ID, token);

                assignments.add(newAssignment);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /*Needed Parcelable Declarations below here*/
    public int describeContents(){
        return 0;
    }

    public void writeToParcel(Parcel out, int flag){
        out.writeInt(ID);
        out.writeString(name);
        out.writeDouble(weight);
        out.writeTypedList(assignments);
    }

    public WeightedGrades(Parcel in) {
        this();

        ID = in.readInt();
        name = in.readString();
        weight = in.readDouble();
        in.readTypedList(assignments, Assignment.CREATOR);
    }

    public static final Parcelable.Creator<WeightedGrades> CREATOR = new Parcelable.Creator<WeightedGrades>() {
        public WeightedGrades createFromParcel(Parcel in) {
            return new WeightedGrades(in);
        }

        public WeightedGrades[] newArray(int size) {
            return new WeightedGrades[size];
        }
    };

}