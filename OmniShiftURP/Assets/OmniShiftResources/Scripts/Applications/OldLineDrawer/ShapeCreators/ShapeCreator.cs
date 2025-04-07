using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ShapeCreator : MonoBehaviour
{
    // I will start with a square and add different ones once I figured out the shape recongnition part
    [SerializeField]
    private GameObject shapePrefab;
    [SerializeField]
    private GameObject planePrefab;
    [SerializeField]
    private GameObject heartPrefab;

    // use this to get the lines
    //public LineController lineController;

    public Transform objectParent;
    public List<GameObject> createdObjects;

    //public enum TestShape { Cube, Plane}
    //public TestShape testShape = TestShape.Cube;


    [Header("Shape recognition")]
    public ShapeRecognition shapeRec;

    //public Shape[] shapes;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // DO NOT USE THIS: instead call function from lineDrawer or lineController class whenever a line was finished
    // Update is called once per frame
    void Update()
    {
        
    }




    /// <summary>
    /// recognizes and creates a shape out of the given lines. If no shape is recognized, nothing happens. 
    /// Return true if shape was created otherwise returns false.
    /// </summary>
    /// <param name="lines"></param>
    public bool CreateShape(LineRenderer line)
    {
        string shape = "";

        List<LineRenderer> lines = new List<LineRenderer>();
        lines.Add(line);

        shape = shapeRec.CheckForShape(lines);

        switch (shape)
        {
            case "Square":
                // Create square shape
                Debug.Log("Square should be instantiated");
                CreateUnrotatedShape(planePrefab, ReturnPointsFromLines(lines), 0.1f);
                return true;
            case "Heart":
                Debug.Log("Heart should be instantiated");
                CreateUnrotatedShape(heartPrefab, ReturnPointsFromLines(lines), 0.5f);
                return true;
            case "No gesture found":
                Debug.Log("No gesture found");
                return false;
            default:
                //DefaultShape(lines);
                break;
        }

        return false;
    }


    /// <summary>
    /// recognizes and creates a shape out of the given lines. If no shape is recognized, nothing happens. 
    /// Return true if shape was created otherwise returns false.
    /// </summary>
    /// <param name="lines"></param>
    public bool CreateShape(List<LineRenderer> lines)
    {
        string shape = "";
        shape = shapeRec.CheckForShape(lines);

        switch (shape)
        {
            case "Square":
                // Create square shape
                Debug.Log("Square should be instantiated");
                CreateUnrotatedShape(planePrefab, ReturnPointsFromLines(lines), 0.1f);
                return true;
            case "Heart":
                Debug.Log("Heart should be instantiated");
                CreateUnrotatedShape(heartPrefab, ReturnPointsFromLines(lines), 0.5f);
                return true;
            case "No gesture found":
                Debug.Log("No gesture found");
                return false;
            default:
                //DefaultShape(lines);
                break;

        }


        return false;
    }





    //public void CreateShape(Vector3[] points)
    //{




    //    switch (testShape)
    //    {
    //        case TestShape.Cube:
    //            DefaultShape(shapePrefab, points);
    //            break;
    //        case TestShape.Plane:
    //            PlaneShape(planePrefab, points);
    //            break;
    //        default:
    //            DefaultShape(shapePrefab, points);
    //            break;
    //    }
        
    //}


    // make the class later abstract so that it will just call the chosen shape?
    //public void CreateShape(GameObject shapePrefab, Vector3[] points)
    //{

    //    switch (testShape)
    //    {
    //        case TestShape.Cube:
    //            DefaultShape(shapePrefab, points);
    //            break;
    //        case TestShape.Plane:
    //            PlaneShape(planePrefab, points);
    //            break;
    //        default:
    //            DefaultShape(shapePrefab, points);
    //            break;
    //    }



    //    // later: test if shape recognition was above certain percentage before calling this function

    //    // get points from lines
    //    // to decide: should only one line or all lines matter?
    //    // try all lines first

    //    // call single drawing classes depending on what recognition said
    //    // probably easier since different shapes might require different transformation

    //    // use default method if no specific transformation is necessary: change size until points fit

    //    // instantiate shapePrefab with size and rotation(?) that fits the points
    //    // probably best via bounds
    //    // there is also geometry3Sharp: https://github.com/gradientspace/geometry3Sharp

    //}


    /// <summary>
    /// This function performs the default transformation of changing the size until all points are included.
    /// It then creates the given shape with identity rotation.
    /// </summary>
    private void DefaultShape(Vector3[] points)
    {
        Bounds bounds = GeometryUtility.CalculateBounds(points, transform.localToWorldMatrix);
        GameObject tmpObj = Instantiate(shapePrefab, bounds.center, shapePrefab.transform.rotation, objectParent);
        tmpObj.transform.localScale = bounds.size;

        createdObjects.Add(tmpObj);
    }

    /// <summary>
    /// This function performs the default transformation of changing the size until all points are included.
    /// It then creates the given shape with identity rotation.
    /// </summary>
    private void DefaultShape(List<LineRenderer> lines)
    {
        Bounds bounds = GeometryUtility.CalculateBounds(ReturnPointsFromLines(lines), transform.localToWorldMatrix);
        GameObject tmpObj = Instantiate(shapePrefab, bounds.center, shapePrefab.transform.rotation, objectParent);
        tmpObj.transform.localScale = bounds.size;

        createdObjects.Add(tmpObj);
    }



    private Vector3[] ReturnPointsFromLines(List<LineRenderer> lines)
    {
        List<Vector3> allPoints = new List<Vector3>();

        foreach(LineRenderer line in lines)
        {
            Vector3[] points = new Vector3[line.positionCount];
            line.GetPositions(points);

            for(int i = 0; i < points.Length; i++)
            {
                allPoints.Add(points[i]);
            }
        }


        Vector3[] returnPoints = allPoints.ToArray();
        return returnPoints;
    }

    //private void PlaneShape(GameObject shapePrefab, Vector3[] points)
    //{
    //    Bounds bounds = GeometryUtility.CalculateBounds(points, transform.localToWorldMatrix);

    //    //for plane y and z need to be switched
    //    // also need to downscale since plane size 1 is 10 times of a cube
    //    bounds.size = new Vector3(bounds.size.x, bounds.size.z, bounds.size.y) * 0.1f;

    //    Debug.Log("Size: " + bounds.size);

    //    GameObject tmpObj = Instantiate(shapePrefab, bounds.center, shapePrefab.transform.rotation, objectParent);
    //    tmpObj.transform.localScale = bounds.size;

        

    //    createdObjects.Add(tmpObj);
    //}

    //private void HeartShape(GameObject shapePrefab, Vector3[] points)
    //{
    //    Bounds bounds = GeometryUtility.CalculateBounds(points, transform.localToWorldMatrix);

    //    //for plane y and z need to be switched
    //    // also need to downscale since plane size 1 is 10 times of a cube
    //    bounds.size = new Vector3(bounds.size.x, bounds.size.z, bounds.size.y) * 0.1f;

    //    Debug.Log("Size: " + bounds.size);

    //    GameObject tmpObj = Instantiate(shapePrefab, bounds.center, shapePrefab.transform.rotation, objectParent);
    //    tmpObj.transform.localScale = bounds.size;



    //    createdObjects.Add(tmpObj);
    //}

    private void CreateUnrotatedShape(GameObject shapePrefab, Vector3[] points, float ratio)
    {
        Bounds bounds = GeometryUtility.CalculateBounds(points, transform.localToWorldMatrix);

        //for plane y and z need to be switched
        // also need to downscale since plane size 1 is 10 times of a cube
        bounds.size = new Vector3(bounds.size.x, bounds.size.z, bounds.size.y) * ratio;

        //Debug.Log("Size: " + bounds.size);
        //Debug.Log("Posiiton: " + bounds.center);

        GameObject tmpObj = Instantiate(shapePrefab, objectParent.InverseTransformPoint(bounds.center), shapePrefab.transform.rotation, objectParent);
        tmpObj.transform.localScale = bounds.size;



        createdObjects.Add(tmpObj);
    }

    

    public void DestroyLines(List<LineRenderer> lines)
    {
        foreach(LineRenderer line in lines)
        {
            Destroy(line.gameObject);
            
        }
    }
}
