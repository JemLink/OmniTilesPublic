using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// this script will instantiate automatically a flower upon detecting a certain pose on the hand that makes the pose
/// </summary>
public class FlowerController : HandBehavior
{
    public List<GameObject> flowers;
    public Vector3 windDirection;

    [Tooltip("This is used to determine the joint the flower will appear at")]
    public int jointID;


    //public bool blooming;

    public GameObject flowerSystemPrefab;
    //public List<Hand> handsWithFlower;


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

            if(flowers.Count == handRep.hands.Count)
            {
                UpdateFlowers();

            }
            else if (flowers.Count < handRep.hands.Count)
            {
                UpdateFewerFlowers();
            }
            else if (flowers.Count > handRep.hands.Count)
            {
                UpdateFewerHands();
            }
            
        }
    }

    public void CreateFlowerAt(Vector3 position)
    {


        flowers.Add(Instantiate(flowerSystemPrefab, position, flowerSystemPrefab.transform.rotation, this.transform));

    }


    private void UpdateFlowers()
    {
        List<Hand> updatedHand = new List<Hand>();

        // Update flower pos
        foreach (GameObject flower in flowers)
        {
            Hand tmpHand = GetNextHand(flower.transform, updatedHand);
            updatedHand.Add(tmpHand);
            flower.GetComponentInChildren<Flower>().UpdatePosition(tmpHand.jointsRep[jointID].transform);
        }
    }


    private void UpdateFewerFlowers()
    {
        List<Hand> handsWithFlowers = new List<Hand>();

        // update flowers to closest hand
        foreach (GameObject flower in flowers)
        {
            Hand tmpHand = GetNextHand(flower.transform, handsWithFlowers);
            handsWithFlowers.Add(tmpHand);
            flower.GetComponentInChildren<Flower>().UpdatePosition(tmpHand.jointsRep[jointID].transform);
        }


        foreach (Hand hand in handRep.hands)
        {
            if (!handsWithFlowers.Contains(hand))
            {
                CreateFlowerAt(hand.joints[jointID]);
            }
        }
    }

    private void UpdateFewerHands()
    {
        List<Flower> flowersWithHands = new List<Flower>();

        foreach (Hand hand in handRep.hands)
        {
            Flower nextFlower = GetNextFlower(hand.jointsRep[jointID].transform, flowersWithHands);
            nextFlower.UpdatePosition(hand.jointsRep[jointID].transform);
            flowersWithHands.Add(nextFlower);
        }

        List<GameObject> flowersToRemove = new List<GameObject>();

        foreach (GameObject flower in flowers)
        {
            if (!flowersWithHands.Contains(flower.GetComponentInChildren<Flower>()))
            {
                flower.GetComponentInChildren<Flower>().StartWithering(windDirection);
                flowersToRemove.Add(flower);
            }
        }

        foreach (GameObject flower in flowersToRemove)
        {
            flowers.Remove(flower);
        }
    }




    /// <summary>
    /// Gets the closes flower to the given Transform this script is attached to except for the flowers included in the list
    /// If no flower is found it returns null
    /// </summary>
    /// <returns></returns>
    protected Flower GetNextFlower(Transform targetPos, List<Flower> excludedFlowers)
    {
        float minDis = Mathf.Infinity;
        Flower closestFlower = null;

        foreach (GameObject flower in flowers)
        {
            if (!excludedFlowers.Contains(flower.GetComponentInChildren<Flower>()))
            {
                float dist = Vector3.Distance(targetPos.position, flower.transform.position);

                if (dist < minDis)
                {
                    minDis = dist;
                    closestFlower = flower.GetComponentInChildren<Flower>();
                }
            }
            
        }

        return closestFlower;
    }
}
