// Call func for each element in the array
// and remove it if the function returns true.
// The list is iterated in reverse order.
function removeif(arr, func)
{
    for(var i=arr.length; i >= 0; i--) {
	if(func(arr[i])) {
	    arr.splice(i, 1);
	}
    }
}
