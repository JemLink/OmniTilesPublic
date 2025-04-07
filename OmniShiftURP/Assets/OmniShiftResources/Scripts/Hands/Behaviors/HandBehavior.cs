using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HandBehavior : MonoBehaviour {

    public HandRepresentation handRep;

    [Tooltip("This decides whether or not the behavior of this script is performed. Use this later to decide via gesture which behavior is active")]
    public bool active;

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    /// <summary>
    /// Gets the closes hand to the object this script is attached to.
    /// If no hand is found it returns null
    /// </summary>
    /// <returns></returns>
    protected Hand GetNextHand()
    {
        float minDis = Mathf.Infinity;
        Hand closestHand = null;

        foreach(Hand hand in handRep.hands)
        {
            float dist = Vector3.Distance(this.transform.position, hand.joints[0]);

            if(dist < minDis)
            {
                minDis = dist;
                closestHand = hand;
            }
        }

        return closestHand;
    }

    /// <summary>
    /// Gets the closes hand to the given Transform this script is attached to.
    /// If no hand is found it returns null
    /// </summary>
    /// <returns></returns>
    protected Hand GetNextHand(Transform targetPos)
    {
        float minDis = Mathf.Infinity;
        Hand closestHand = null;

        foreach (Hand hand in handRep.hands)
        {
            float dist = Vector3.Distance(targetPos.position, hand.joints[0]);

            if (dist < minDis)
            {
                minDis = dist;
                closestHand = hand;
            }
        }

        return closestHand;
    }

    /// <summary>
    /// Gets the closes hand to the given Transform this script is attached to and ignores all hands included in the list.
    /// If no hand is found it returns null
    /// </summary>
    /// <returns></returns>
    protected Hand GetNextHand(Transform targetPos, List<Hand> excludedHands)
    {
        float minDis = Mathf.Infinity;
        Hand closestHand = null;

        foreach (Hand hand in handRep.hands)
        {
            if (!excludedHands.Contains(hand))
            {
                float dist = Vector3.Distance(targetPos.position, hand.joints[0]);

                if (dist < minDis)
                {
                    minDis = dist;
                    closestHand = hand;
                }
            }
            
        }

        return closestHand;
    }

    protected Hand GetSingleHand(int id)
    {
        return handRep.hands[id];

    }
}
