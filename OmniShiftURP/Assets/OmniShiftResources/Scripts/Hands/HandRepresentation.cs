using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;



/// <summary>
/// This class has the overview of all hands in the scene and updates their positions via calling the local functions in the hand script
/// 
/// </summary>
public class HandRepresentation : MonoBehaviour
{


    /*
     * Mediapipes indexing is as follows:
     * 0: wrist                     13: ring_MCP
     * 1: thumb_CMC                 14: ring_PIP
     * 2: thumb_MCP                 15: ring_DIP
     * 3: thumb_IP                  16: ring_TIP
     * 4: thumb_TIP                 17: pinky_MCP
     * 5: index_MCP                 18: pinky_PIP
     * 6: index_PIP                 19: pinky_DIP
     * 7: index_DIP                 20: pinky_TIP
     * 8: index_TIP
     * 9: middle_MCP
     * 10: middle_PIP
     * 11: middle_DIP
     * 12: middle_TIP
     * 
     * */

    //public Vector3[] jointsArray;
    public List<Hand> hands = new List<Hand>();
    public Hand handRepresentation;

    //public Hand[] hands;

    //// Add more gestures in here when the model is trained for them
    //// NOTE: They should be in the same order as in the training model
    //public enum Gesture { Open, Closed, Pointer}
    //public Gesture gesture;

    //public int gestureID;
    public bool handDetected = false;

    [Tooltip("This is the minimum distance to joints of two hands should have to be detected as two")]
    public float minHandsDistance;


    #region Update joint position



    public void UpdateHandPose(string message)
    {

        //reset hands list
        //hands.Clear();

        // test if message has gesture (-1 is sent in case that no hand was detected)
        if (message.StartsWith("-1"))
        {
            //Debug.Log("NO hand detected");
            handDetected = false;

            DestroyHands();
        }
        else
        {

            // first need to divide all hands
            // they are separated via h for hand
            string[] handsStr = GetSingleHands(message);


            // make sure that handsStr and hands have same size by adding or removing hands from the list

            while (handsStr.Length < hands.Count)
            {
                Hand tmpHand = hands[0];
                hands[0].DestroyHand();
                hands.Remove(tmpHand);

                Destroy(tmpHand.gameObject);


            }

            while (handsStr.Length > hands.Count)
            {
                hands.Add(Instantiate(handRepresentation, this.transform));
            }




            List<Hand> handsToRemove = new List<Hand>();

            for (int i = 0; i < hands.Count; i++)
            {
                hands[i].UpdateHandPos(handsStr[i]);


                // make sure that none of the hands in within each other
                for (int j = 0; j < i; j++)
                {
                    int handsEnclosed = HandsInEachOther(hands[i], hands[j]);

                    switch (handsEnclosed)
                    {
                        case 0:
                            // no hand needs to be removed
                            break;
                        case 1:
                            // hand 2 needs to be removed
                            handsToRemove.Add(hands[j]);
                            Debug.Log("Removed hand j");
                            break;
                        case 2:
                            // hand 1 needs to be removed
                            handsToRemove.Add(hands[i]);
                            Debug.Log("Removed hand i");
                            break;
                        default:
                            Debug.LogError("Something went wrong in switch case statement");
                            break;
                    }


                }

            }


            foreach (Hand handToRem in handsToRemove)
            {
                hands.Remove(handToRem);
                handToRem.DestroyHand();
                Destroy(handToRem.gameObject);

            }



        }




    }



    public void DestroyHands()
    {
        Hand tmpHand;

        while (hands.Count > 0)
        {
            tmpHand = hands[0];

            hands[0].DestroyHand();


            hands.Remove(tmpHand);

            Destroy(tmpHand.gameObject);
        }

    }




    /// <summary>
    /// This will retrieve all hand strings with the single hand coordinates in it
    /// </summary>
    /// <param name="message"></param>
    private string[] GetSingleHands(string message)
    {
        string[] hands = message.Split('h');

        // since the python message should always end with an h we need to get rid of the last string
        string[] returnString = new string[hands.Length - 1];

        for (int i = 0; i < returnString.Length; i++)
        {
            returnString[i] = hands[i];
        }

        return returnString;
    }



    private bool HandsToClose(Hand hand1, Hand hand2)
    {
        for (int i = 0; i < hand1.joints.Length; i++)
        {
            if (Vector3.Distance(hand1.joints[i], hand2.joints[i]) < minHandsDistance)
            {
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// This funciton returns 
    /// 0 if the hands do not collide
    /// 1 if hand1 contains hand2
    /// 2 if hand2 contains hand1
    /// </summary>
    /// <param name="hand1"></param>
    /// <param name="hand2"></param>
    /// <returns></returns>
    private int HandsInEachOther(Hand hand1, Hand hand2)
    {
        // first check if hands are close
        if (HandsToClose(hand1, hand2))
        {
            // now check if they actually encapuslate each other
            bool hand1Contains2 = ColliderContains(hand1.handCollider, hand2.handCollider.center);
            bool hand2Contains1 = ColliderContains(hand2.handCollider, hand1.handCollider.center);
            bool handsInEachOther = hand2Contains1 || hand1Contains2;

            if (handsInEachOther)
            {
                // Get extends of both colliders
                Vector3 hand1Extends = hand1.handCollider.bounds.extents;
                float hand1MaxExtend = Mathf.Max(hand1Extends.x, hand1Extends.y, hand1Extends.z);

                Vector3 hand2Extends = hand2.handCollider.bounds.extents;
                float hand2MaxExtend = Mathf.Max(hand2Extends.x, hand2Extends.y, hand2Extends.z);

                // check which collider box is bigger (since this should be the one encapsulating the inner one)
                if (hand1MaxExtend > hand2MaxExtend)
                {
                    return 1;
                }
                else
                {
                    return 2;
                }
            }

        }

        return 0;




    }


    public bool ColliderContains(Collider col, Vector3 point)
    {
        Vector3 colCenter = col.transform.InverseTransformPoint(col.bounds.center);
        Vector3 colExtents = col.bounds.extents;

        bool containsX = ((colCenter.x - colExtents.x) < point.x) && ((colCenter.x + colExtents.x) > point.x);
        bool containsY = ((colCenter.y - colExtents.y) < point.y) && ((colCenter.y + colExtents.y) > point.y);
        //bool containsZ = ((colCenter.z - colExtents.z) < point.z) && ((colCenter.z + colExtents.z) > point.z);


        if (containsX && containsY)// && containsZ)
        {
            return true;
        }
        else
        {
            return false;
        }
    }


    #endregion



}
