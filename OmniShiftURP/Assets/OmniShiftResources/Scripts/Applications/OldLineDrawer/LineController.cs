using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LineController : HandBehavior
{

    public GameObject LineDrawerPrefab;
    public List<GameObject> lineDrawers;

    public Transform linesParent;
    private List<GameObject> lines = new List<GameObject>();

    [Header("Shape Recognition")]
    [Tooltip("This is the threshold for how long a line needs to be to perform shape recognition")]
    public int pointThreshold;
    public ShapeCreator shapeCreator;
    public bool recognitionActive;


    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (active)
        {
            // check if number of hands and number of flowers is equal

            if (lineDrawers.Count == handRep.hands.Count)
            {
                UpdateLines();

            }
            else if (lineDrawers.Count < handRep.hands.Count)
            {
                UpdateFewerLines();
            }
            else if (lineDrawers.Count > handRep.hands.Count)
            {
                UpdateFewerHands();
            }

        }
    }


    private void UpdateLines()
    {
        List<Hand> updatedHand = new List<Hand>();

        // Update the hand object of the lines
        foreach (GameObject lineDrawer in lineDrawers)
        {
            Hand tmpHand = GetNextHand(lineDrawer.gameObject.transform, updatedHand);
            updatedHand.Add(tmpHand);
            lineDrawer.transform.position = tmpHand.joints[8];
            lineDrawer.GetComponentInChildren<LineDrawer>().hand = tmpHand;
        }
    }


    private void UpdateFewerLines()
    {
        List<Hand> handsWithDrawers = new List<Hand>();

        // update flowers to closest hand
        foreach (GameObject drawer in lineDrawers)
        {
            Hand tmpHand = GetNextHand(drawer.gameObject.transform, handsWithDrawers);
            handsWithDrawers.Add(tmpHand);
            drawer.gameObject.transform.position = tmpHand.joints[8];
            drawer.GetComponentInChildren<LineDrawer>().hand = tmpHand;
            
        }


        foreach (Hand hand in handRep.hands)
        {
            if (!handsWithDrawers.Contains(hand))
            {
                CreateLineDrawer(hand);
                
            }
        }
    }


    private void UpdateFewerHands()
    {
        List<LineDrawer> drawersWithHands = new List<LineDrawer>();

        foreach (Hand hand in handRep.hands)
        {
            LineDrawer nextDrawer = GetNextDrawer(hand.jointsRep[8].transform, drawersWithHands);
            nextDrawer.transform.position = hand.joints[8];
            nextDrawer.hand = hand;

            drawersWithHands.Add(nextDrawer);
        }

        List<GameObject> drawersToRemove = new List<GameObject>();

        foreach (GameObject drawer in lineDrawers)
        {
            if (!drawersWithHands.Contains(drawer.GetComponentInChildren<LineDrawer>()))
            {
                drawersToRemove.Add(drawer);
            }
        }

        foreach (GameObject drawer in drawersToRemove)
        {
            lineDrawers.Remove(drawer);
            Destroy(drawer);
        }
    }




    /// <summary>
    /// Gets the closes flower to the given Transform this script is attached to except for the flowers included in the list
    /// If no flower is found it returns null
    /// </summary>
    /// <returns></returns>
    protected LineDrawer GetNextDrawer(Transform targetPos, List<LineDrawer> excludedDrawers)
    {
        float minDis = Mathf.Infinity;
        LineDrawer closestDrawer = null;

        foreach (GameObject drawer in lineDrawers)
        {
            if (!excludedDrawers.Contains(drawer.GetComponentInChildren<LineDrawer>()))
            {
                float dist = Vector3.Distance(targetPos.position, drawer.transform.position);

                if (dist < minDis)
                {
                    minDis = dist;
                    closestDrawer = drawer.GetComponentInChildren<LineDrawer>();
                }
            }

        }

        return closestDrawer;
    }


    private void CreateLineDrawer(Hand hand)
    {
        GameObject tmpDrawer = Instantiate(LineDrawerPrefab, gameObject.transform);
        tmpDrawer.GetComponentInChildren<LineDrawer>().hand = hand;
        tmpDrawer.GetComponentInChildren<LineDrawer>().lineController = this;

        lineDrawers.Add(tmpDrawer);
    }


    public void AddLineToLines(GameObject line)
    {
        lines.Add(line);
    }

    public void TryRecognizingShape(GameObject line)
    {
        //only check line if it contains more points

        if (line.GetComponent<LineRenderer>().positionCount > pointThreshold)
        {
            //Debug.Log("Try to recognize shape");


            if (recognitionActive && shapeCreator)
            {
                if (shapeCreator.CreateShape(line.GetComponent<LineRenderer>()))
                {
                    RemoveLineFromLines(line);
                    Destroy(line);
                }
            }
        }

    }

    public void RemoveLineFromLines(GameObject lineToRemove)
    {
        lines.Remove(lineToRemove);
    }

    public List<GameObject> GetLines()
    {
        return lines;
    }
}
