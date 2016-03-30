app.controller('DocumentController', function ($scope, $http, $location, $routeParams) {
    /************************************************************************************************
     * Properties
     */
    $scope.doc_id = $routeParams.doc_id;

    $scope.model = {};
    $scope.keywords = [];
    $scope.closest = [];
    $scope.columns = [];

    $scope.hideExtraDetails = true;
    $scope.loading = true;

    /************************************************************************************************
    * Data Model Methods
    */

    $scope.onModelLoaded = function (data) {
        $scope.model = data;
        if ($scope.model == null) {
            $scope.model = {};
            return;
        }

        // Make the dates user-friendly
        $scope.model.scannedAsDate = new Date($scope.model.scanned).toLocaleString();
        $scope.model.createdAsDate = new Date($scope.model.dateCreated).toLocaleString();

        $scope.request($scope.apiUrl + '/keywords', $scope.onKeywordsLoaded);
    }

    $scope.onKeywordsLoaded = function (data) {
        $scope.request($scope.apiUrl + '/closest', $scope.onClosestLoaded);

        $scope.keywords = {};
        data.forEach(function (e) {
            $scope.keywords[e.lemma] = {};
            $scope.keywords[e.lemma][$scope.doc_id] = e.score;
        });
    }

    $scope.onClosestLoaded = function (data) {
        $scope.closest = data;
        if ($scope.closest == null) {
            $scope.closest = [];
        }

        data.forEach(function (doc) {
            Object.keys(doc.scores).forEach(function (w) {
                var scores = doc.scores[w]

                if (!(w in $scope.keywords)) {
                    $scope.keywords[w] = {};
                    $scope.keywords[w][$scope.doc_id] = scores[$scope.doc_id];
                }

                Object.keys(scores).forEach(function (id) {
                    if (id != $scope.doc_id)
                        $scope.keywords[w][id] = scores[id];
                });
            });

            if ("links" in doc) {
                // Pop the 'View/Edit' link as the primary
                var elem = doc["links"].shift();
                doc["view"] = elem.href.replace('/api/v1/', '/');

                // Fix the urls
                angular.forEach(doc["links"], function (link) {
                    link.href = link.href.replace('/api/v1/', '/');
                });
            }
        });

        var cols = Object.keys($scope.keywords)
        cols.sort(function (a, b) {
            var av = $scope.keywords[a][$scope.doc_id];
            var bv = $scope.keywords[b][$scope.doc_id];
            if (av > bv) {
                return -1; // reverse sort
            }
            if (av < bv) {
                return 1; // reverse sort
            }
            return 0;
        });

        $scope.columns = cols;
        $scope.loading = false;
    }

    /************************************************************************************************
     * Actions
     */

    /************************************************************************************************
     * Methods
     */

    $scope.buildUrl = function () {
        url = 'http://' + $location.host() + ':' + $location.port() + '/api/v1' + $location.url()
        return url;
    };

    $scope.request = function (url, callback) {
        $http.get(url)
            .then(function (response) {
                callback(response.data)
            }, function (response) {
                alert(response.status)
            });
    }

    /************************************************************************************************
     * Initialization
     */

    $scope.apiUrl = $scope.buildUrl();

    $scope.keywordsUrl = $location.url() + '/keywords?limit=20'
    $scope.closestUrl = $location.url() + '/closest?limit=20'

    $scope.request($scope.apiUrl, $scope.onModelLoaded);
});